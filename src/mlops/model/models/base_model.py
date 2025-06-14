from abc import ABC, abstractmethod
from pathlib import Path

import numpy.typing as npt
import pandas as pd

type PdNpType = pd.DataFrame | npt.NDArray


class BaseModel(ABC):
    @abstractmethod
    def train(
        self,
        X_train: PdNpType,
        y_train: PdNpType,
        X_valid: PdNpType,
        y_valid: PdNpType,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def predict_proba(self, X: PdNpType) -> npt.NDArray:
        raise NotImplementedError

    @abstractmethod
    def save(self, file_path: Path) -> None:
        raise NotImplementedError

    @classmethod
    def from_pretrained(cls, s3_key: str) -> "BaseModel":
        raise NotImplementedError
