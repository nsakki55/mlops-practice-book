import tempfile
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import pytest

from mlops.model import LightGBMModel


@pytest.fixture
def train_test_data():
    X_train = pd.DataFrame(
        {
            "feature1": [1, 2, 3, 4, 5],
            "feature2": [0.1, 0.2, 0.3, 0.4, 0.5],
            "feature3": pd.Series(["A", "B", "A", "B", "A"], dtype="category"),
        }
    )
    y_train = pd.Series([0, 1, 0, 1, 0])

    X_valid = pd.DataFrame(
        {"feature1": [6, 7, 8], "feature2": [0.6, 0.7, 0.8], "feature3": pd.Series(["B", "A", "B"], dtype="category")}
    )
    y_valid = pd.Series([1, 0, 1])

    return X_train, y_train, X_valid, y_valid


def test_train_with_dataframe(train_test_data):
    X_train, y_train, X_valid, y_valid = train_test_data

    model = LightGBMModel()
    model.train(X_train, y_train, X_valid, y_valid)

    assert model.model is not None
    assert isinstance(model.model, lgb.Booster)


def test_predict_proba_not_instantiated():
    model = LightGBMModel()

    with pytest.raises(ValueError, match="Model is not instantiated"):
        model.predict_proba(np.array([[1, 0.1]]))


def test_predict_proba(train_test_data):
    X_train, y_train, X_valid, y_valid = train_test_data

    model = LightGBMModel()
    model.train(X_train, y_train, X_valid, y_valid)

    X_test = pd.DataFrame({"feature1": [1, 6], "feature2": [0.1, 0.6], "feature3": pd.Series(["B", "A"], dtype="category")})

    predictions = model.predict_proba(X_test)

    assert isinstance(predictions, np.ndarray)
    assert predictions.shape == (2,)
    assert np.all((predictions >= 0) & (predictions <= 1))


def test_save_not_instantiated():
    model = LightGBMModel()

    with pytest.raises(ValueError, match="Model is not instantiated"):
        model.save(Path("test_model.txt"))


def test_save(train_test_data):
    X_train, y_train, X_valid, y_valid = train_test_data

    model = LightGBMModel()
    model.train(X_train, y_train, X_valid, y_valid)

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test_model.txt"
        model.save(file_path)

        assert file_path.exists()

        loaded_model = lgb.Booster(model_file=str(file_path))
        assert isinstance(loaded_model, lgb.Booster)
