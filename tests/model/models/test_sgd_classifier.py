import pickle
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import SGDClassifier

from mlops.model import SGDClassifierModel


@pytest.fixture
def train_test_data():
    X_train = pd.DataFrame(
        {"feature1": [1, 2, 3, 4, 5], "feature2": [0.1, 0.2, 0.3, 0.4, 0.5], "feature3": ["A", "B", "A", "B", "A"]}
    )
    y_train = pd.Series([0, 1, 0, 1, 0])

    X_valid = pd.DataFrame({"feature1": [6, 7, 8], "feature2": [0.6, 0.7, 0.8], "feature3": ["B", "A", "B"]})
    y_valid = pd.Series([1, 0, 1])

    return X_train, y_train, X_valid, y_valid


def test_train(train_test_data, monkeypatch):
    X_train, y_train, X_valid, y_valid = train_test_data

    model = SGDClassifierModel(is_optuna=False, args={"loss": "log_loss", "random_state": 42})
    model.train(X_train, y_train, X_valid, y_valid)

    assert model.model is not None
    assert isinstance(model.model, SGDClassifier)


def test_predict_proba_not_instantiated():
    model = SGDClassifierModel()
    with pytest.raises(ValueError, match="Model is not instantiated"):
        model.predict_proba(pd.DataFrame({"feature1": [1, 2]}))


def test_predict_proba(train_test_data):
    X_train, y_train, X_valid, y_valid = train_test_data

    sgd_classifier_model = SGDClassifierModel(is_optuna=False, args={"loss": "log_loss", "random_state": 42})
    sgd_classifier_model.train(X_train, y_train, X_valid, y_valid)

    X_test = pd.DataFrame({"feature1": [1, 6], "feature2": [0.1, 0.6], "feature3": ["A", "B"]})

    predictions = sgd_classifier_model.predict_proba(X_test)

    assert isinstance(predictions, np.ndarray)
    assert predictions.shape == (2,)
    assert np.all((predictions >= 0) & (predictions <= 1))


def test_save_not_instantiated():
    model = SGDClassifierModel()

    with pytest.raises(ValueError):
        model.save(Path("test_model.pkl"))


def test_save(train_test_data):
    X_train, y_train, X_valid, y_valid = train_test_data

    model = SGDClassifierModel(is_optuna=False, args={"loss": "log_loss", "random_state": 42})
    model.train(X_train, y_train, X_valid, y_valid)

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test_model.pkl"
        model.save(file_path)

        assert file_path.exists()

        with open(file_path, "rb") as f:
            loaded_model = pickle.load(f)
        assert isinstance(loaded_model, SGDClassifier)
