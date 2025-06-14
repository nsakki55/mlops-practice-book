import logging
import pickle
import tempfile
from pathlib import Path

import numpy as np
import numpy.typing as npt
import optuna
import pandas as pd
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import log_loss

from mlops.aws import download_file_from_s3
from mlops.const import MODEL_S3_BUCKET

from .base_model import BaseModel, PdNpType

logger = logging.getLogger(__name__)


class SGDClassifierModel(BaseModel):
    def __init__(
        self,
        model: SGDClassifier | None = None,
        is_optuna: bool = True,
        args: dict | None = None,
    ) -> None:
        self.model = model
        self.is_optuna = is_optuna
        self.args = args if args else {}

    def train(
        self,
        X_train: PdNpType,
        y_train: PdNpType,
        X_valid: PdNpType,
        y_valid: PdNpType,
    ) -> None:
        X_train_hashed = hashing_feature(X_train)
        X_valid_hashed = hashing_feature(X_valid)
        _args = self.args
        if self.is_optuna:
            best_alpha = self._optuna_search(X_train_hashed, y_train, X_valid_hashed, y_valid)
            _args["alpha"] = best_alpha
        model = SGDClassifier(**_args)
        model.fit(X_train_hashed, y_train)
        self.model = model

    def predict_proba(self, X: PdNpType) -> npt.NDArray:
        if self.model is None:
            raise ValueError("Model is not instantiated.")
        X_hashed = hashing_feature(X)
        y_pred = self.model.predict_proba(X_hashed)[:, 1]
        return y_pred

    def save(self, file_path: Path) -> None:
        logger.info(f"Save model file at {file_path}.")
        if self.model is None:
            raise ValueError("Model is not instantiated.")

        with open(file_path, "wb") as f:
            pickle.dump(self.model, f)

    def _optuna_search(
        self,
        X_train: PdNpType,
        y_train: PdNpType,
        X_valid: PdNpType,
        y_valid: PdNpType,
    ) -> float:
        def objective(trial: optuna.trial._trial.Trial) -> float:
            max_alpha = 0.0001
            alpha = trial.suggest_float("alpha", 0, max_alpha)
            model = SGDClassifier(loss="log_loss", penalty="l2", random_state=42, alpha=alpha)

            model.fit(X_train, y_train)
            y_pred = model.predict_proba(X_valid)[:, 1]
            score = log_loss(y_true=y_valid, y_pred=y_pred)

            return float(score)

        logger.info("Started Hyper Parameter by optuna")
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=10)

        best_score = study.best_value
        best_alpha = study.best_params["alpha"]
        logger.info(f"Started Hyper Parameter by optuna. {best_alpha=}, {best_score=}")
        return best_alpha

    @classmethod
    def from_pretrained(
        cls,
        s3_key: str,
    ) -> "SGDClassifierModel":
        logger.info(f"Loading model from s3://{MODEL_S3_BUCKET}/{s3_key}")
        with tempfile.NamedTemporaryFile() as temp_file:
            download_file_from_s3(
                s3_bucket=MODEL_S3_BUCKET,
                s3_key=s3_key,
                file_path=temp_file.name,
            )

            with open(temp_file.name, "rb") as f:
                model = pickle.load(f)
        return cls(model)


def hashing_feature(df: pd.DataFrame, hash_size: int = 2**18) -> npt.NDArray:
    feature_hasher = FeatureHasher(n_features=hash_size, input_type="string")
    hashed_feature = feature_hasher.fit_transform(np.asanyarray(df.astype(str)))
    return hashed_feature
