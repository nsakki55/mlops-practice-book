import json
import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, Request

from mlops.aws import OnlineFeatureStoreDynamoDB, get_latest_model_version, get_model_s3_key
from mlops.const import FEATURE_DYNAMODB_TABLE, MODEL_REGISTRY_DYNAMODB_TABLE
from mlops.middleware import Artifact, set_logger_config
from mlops.model import add_impression_time_feature, get_model_config
from mlops.predictor import AdRequest

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    current_time = datetime.now()
    version = current_time.strftime("%Y%m%d%H%M%S")
    artifact = Artifact(version=version, job_type="predictor")
    set_logger_config(log_file_path=artifact.file_path("log.txt"))

    # Setup for model config
    model_name = os.getenv("MODEL_NAME", "sgd_classifier_ctr")
    model_version = os.getenv("MODEL_VERSION", "latest")
    feature_version = os.getenv("FEATURE_VERSION", "latest")
    logger.info(f"Configure {model_name=}, {model_version=}, {feature_version=}")

    if model_version == "latest":
        latest_model_version = get_latest_model_version(table=MODEL_REGISTRY_DYNAMODB_TABLE, model=model_name)
        if latest_model_version is None:
            raise ValueError("No latest model found")
        model_version = latest_model_version

    model_s3_key = get_model_s3_key(table=MODEL_REGISTRY_DYNAMODB_TABLE, model=model_name, version=model_version)
    if model_s3_key is None:
        raise ValueError("Model S3 key not found")

    model_config = get_model_config(model_name=model_name)
    model = model_config.model_class.from_pretrained(s3_key=model_s3_key)

    online_feature_store = OnlineFeatureStoreDynamoDB(table=FEATURE_DYNAMODB_TABLE, version=feature_version)

    def log_prediction(df: pd.DataFrame, prediction: float) -> None:
        df = df.assign(
            prediction=prediction,
            model_name=model_name,
            model_version=model_version,
            feature_version=feature_version,
            logged_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        print(json.dumps(df.iloc[0].to_dict()))

    yield {
        "model": model,
        "model_config": model_config,
        "online_feature_store": online_feature_store,
        "log_prediction": log_prediction,
    }


app = FastAPI(lifespan=lifespan)


@app.post("/predict")
async def predict(ad_request: AdRequest, request: Request) -> dict[str, str | float]:
    df = pd.DataFrame([ad_request.model_dump()])

    # Get user feature from DynamoDB
    user_feature = request.state.online_feature_store.get_impression_feature(user_id=ad_request.user_id)
    df = df.assign(**user_feature)

    # Add impression time features
    df = add_impression_time_feature(df, "logged_at")

    # Fill missing values and convert data types
    for schema in request.state.model_config.schemas:
        if schema.name not in df.columns:
            df[schema.name] = np.nan
        df[schema.name] = df[schema.name].fillna(schema.null_value)
        df[schema.name] = df[schema.name].astype(schema.dtype)
    df = df[[schema.name for schema in request.state.model_config.schemas]]

    # Get prediction
    prediction = request.state.model.predict_proba(df)

    request.state.log_prediction(df, float(prediction))

    return dict(
        model=request.state.model_config.name,
        prediction=float(prediction),
    )


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"health": "ok"}


def main() -> None:
    uvicorn.run("predictor:app", host="0.0.0.0", port=8080, reload=True)


if __name__ == "__main__":
    main()
