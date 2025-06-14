import argparse
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime

from mlops.aws import (
    get_latest_model_version,
    get_model_s3_key,
    register_model_registry,
    run_task,
    upload_dir_to_s3,
    upload_file_to_s3,
)
from mlops.const import MODEL_REGISTRY_DYNAMODB_TABLE, MODEL_S3_BUCKET
from mlops.data_loader import compose_sql, extract_dataframe_from_athena
from mlops.evaluation import (
    calculate_metrics,
    is_model_better_than_baseline,
    plot_calibration_curve,
    plot_histgram,
    plot_roc_auc_curve,
)
from mlops.middleware import Artifact, set_logger_config
from mlops.model import (
    MetaDeta,
    add_impression_time_feature,
    apply_schema,
    apply_train_test_split,
    get_model_config,
)

logger = logging.getLogger(__name__)


def load_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ML pipeline arguments")
    parser.add_argument("-m", "--model_name", type=str, default="sgd_classifier_ctr")
    parser.add_argument("-t", "--feature_version", type=str, default="20250614130717")
    parser.add_argument("--ecs", action="store_true")
    parser.add_argument("--cpu", type=int, default=1024)
    parser.add_argument("--memory", type=int, default=2048)

    return parser.parse_args()


def main() -> None:
    args = load_options()

    # -----------------------------
    # Run Train Pipeline as ECS Task
    # -----------------------------
    if args.ecs:
        run_task(command=sys.argv, cpu=args.cpu, memory=args.memory)
        return

    # -----------------------------
    # Setup
    # -----------------------------
    current_time = datetime.now()
    version = current_time.strftime("%Y%m%d%H%M%S")
    artifact = Artifact(version=version, job_type=f"train/{args.model_name}")
    set_logger_config(log_file_path=artifact.file_path("log.txt"))
    model_config = get_model_config(model_name=args.model_name)
    logger.info(f"{artifact=}, {args=}, {vars(model_config)=}")

    # -----------------------------
    # Preprocess Data
    # -----------------------------
    sql_impression_feature = compose_sql(
        table="impression_feature", additional_where_clause=f"version='{args.feature_version}'"
    )
    df_impression_feature = extract_dataframe_from_athena(sql=sql_impression_feature)
    df_preprocessed = add_impression_time_feature(df_impression_feature, "logged_at")
    df_preprocessed = apply_schema(df=df_preprocessed, schemas=model_config.schemas)
    df_train, df_valid, df_test = apply_train_test_split(df=df_preprocessed, **model_config.test_valid_ratio)

    # -----------------------------
    # Train Model
    # -----------------------------
    model = model_config.model_class
    model.train(
        X_train=df_train[model_config.feature_columns],
        y_train=df_train[model_config.target],
        X_valid=df_valid[model_config.feature_columns],
        y_valid=df_valid[model_config.target],
    )

    # -----------------------------
    # Evaluate Model
    # -----------------------------
    train_metrics = calculate_metrics(
        y_true=df_train[model_config.target], y_pred=model.predict_proba(X=df_train[model_config.feature_columns])
    )

    y_pred = model.predict_proba(X=df_test[model_config.feature_columns])
    y_test = df_test[model_config.target]
    test_metrics = calculate_metrics(
        y_true=df_test[model_config.target],
        y_pred=y_pred,
    )
    metrics = dict(train=train_metrics, test=test_metrics)

    fig_calibration_curve = plot_calibration_curve(
        y_true=y_test,
        y_pred=y_pred,
    )
    fig_roc_auc_curve = plot_roc_auc_curve(
        y_true=y_test,
        y_pred=y_pred,
    )
    fig_histgram = plot_histgram(
        y_true=df_test[model_config.target],
        y_pred=y_pred,
    )

    latest_model_version = get_latest_model_version(table=MODEL_REGISTRY_DYNAMODB_TABLE, model=model_config.name)
    if latest_model_version is None:
        is_update_model_version = True
    else:
        model_s3_key = get_model_s3_key(
            table=MODEL_REGISTRY_DYNAMODB_TABLE,
            model=model_config.name,
            version=latest_model_version,
        )
        if model_s3_key is None:
            raise ValueError("Model S3 key not found")
        latest_model = model_config.model_class.from_pretrained(s3_key=model_s3_key)
        y_baseline = latest_model.predict_proba(X=df_test[model_config.feature_columns])
        is_update_model_version = is_model_better_than_baseline(
            y_pred=y_pred,
            y_baseline=y_baseline,
            y_true=y_test,
        )

    # -----------------------------
    # Store Artifacts
    # -----------------------------
    # Save metadata
    meta_data = MetaDeta(
        model_config=model_config,
        command_lie_arguments=args,
        version=version,
        start_time=current_time,
        end_time=datetime.now(),
        artifact_key_prefix=artifact.key_prefix,
    )
    meta_data.save_as_json(artifact.file_path("metadata.json"))

    # Save data artifacts
    ## Save preprocessed data
    df_preprocessed.to_csv(artifact.file_path("df_preprocessed.csv"), index=False)

    # Save model
    model.save(artifact.file_path("model.pkl"))

    # Save evaluation result
    with open(artifact.file_path("metrics.csv"), "w") as f:
        json.dump(metrics, f, indent=2)

    fig_calibration_curve.savefig(artifact.file_path("calibration_curve.png"))
    fig_roc_auc_curve.savefig(artifact.file_path("roc_auc_curve.png"))
    fig_histgram.savefig(artifact.file_path("histgram.png"))

    # Upload artifacts to S3
    upload_dir_to_s3(
        s3_bucket=MODEL_S3_BUCKET,
        dir_path=artifact.dir_path,
        key_prefix=artifact.key_prefix,
    )

    # Upload split data to S3
    for data_type, _df in {"train": df_train, "valid": df_valid, "test": df_test}.items():
        _df.to_csv(artifact.file_path(f"df_{data_type}.csv"), index=False)
        partition = f"model_name={model_config.name}/model_version={version}/data_type={data_type}"
        upload_file_to_s3(
            s3_bucket=MODEL_S3_BUCKET,
            file_path=artifact.file_path(f"df_{data_type}.csv"),
            s3_key=f"train_log/{partition}/df_{data_type}.csv",
        )

    # -----------------------------
    # Register Model Registry
    # -----------------------------
    if is_update_model_version:
        register_model_registry(
            table_name=MODEL_REGISTRY_DYNAMODB_TABLE,
            model_name=model_config.name,
            version=version,
            metadata={
                "start_time": meta_data.start_time,
                "end_time": meta_data.end_time,
                "dataset_parameter": {
                    "lookback_days": model_config.lookback_days,
                    "train_interval_days": model_config.train_interval_days,
                    "test_valid_ratio": model_config.test_valid_ratio,
                    "to_datetime": current_time,
                },
                "model_parameter": vars(model_config.model_class),
                "features": [asdict(schema) for schema in model_config.schemas],
                "dependencies": meta_data.dependencies,
                "commandline_arguments": vars(meta_data.command_lie_arguments),
                "branch": meta_data.git_branch,
                "commit_hash": meta_data.git_commit_hash,
                "image_uri": meta_data.image_uri,
                "metrics": metrics,
                "artifact_s3_path": f"{artifact.key_prefix}",
                "model_s3_path": f"{artifact.key_prefix}/model.pkl",
                "tag": {
                    "target": "ctr prediction",
                },
            },
        )

    logger.info(f"Finished ML Pipeline. {meta_data=}")


if __name__ == "__main__":
    main()
