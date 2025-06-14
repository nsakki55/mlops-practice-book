import logging
import tempfile
from pathlib import Path

import lightgbm as lgb
import numpy as np
import numpy.typing as npt
import pandas as pd

from mlops.aws import download_file_from_s3
from mlops.const import MODEL_S3_BUCKET

from .base_model import BaseModel, PdNpType

logger = logging.getLogger(__name__)


class LightGBMModel(BaseModel):
    def __init__(
        self,
        model: lgb.Booster | None = None,
        args: dict | None = None,
        num_round: int = 10,
    ) -> None:
        self.model = model
        if args is None:
            args = {}
        self.args = args | {"objective": "binary"}
        self.num_round = num_round

    def train(
        self,
        X_train: PdNpType,
        y_train: PdNpType,
        X_valid: PdNpType,
        y_valid: PdNpType,
    ) -> None:
        if isinstance(X_train, pd.DataFrame):
            category_columns = X_train.select_dtypes(include=["category"]).columns.tolist()
        train_data = lgb.Dataset(
            X_train,
            label=y_train,
            categorical_feature=category_columns,
        )
        valid_data = lgb.Dataset(
            X_valid,
            label=y_valid,
            categorical_feature=category_columns,
        )
        model = lgb.train(self.args, train_data, self.num_round, valid_sets=[valid_data])
        self.model = model

    def predict_proba(self, X: PdNpType) -> npt.NDArray:
        if self.model is None:
            raise ValueError("Model is not instantiated.")
        y_pred = np.asarray(self.model.predict(X))
        return y_pred

    def save(self, file_path: Path) -> None:
        logger.info(f"Save model file at {file_path}.")
        if self.model is None:
            raise ValueError("Model is not instantiated.")
        self.model.save_model(file_path)

    @classmethod
    def from_pretrained(
        cls,
        s3_key: str,
    ) -> "LightGBMModel":
        logger.info(f"Loading model from s3://{MODEL_S3_BUCKET}/{s3_key}")
        with tempfile.NamedTemporaryFile() as temp_file:
            download_file_from_s3(
                s3_bucket=MODEL_S3_BUCKET,
                s3_key=s3_key,
                file_path=temp_file.name,
            )
            model = lgb.Booster(model_file=temp_file.name)
        return cls(model)
