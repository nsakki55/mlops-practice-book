import numpy as np
from numpy.testing import assert_almost_equal

from mlops.evaluation import calculate_metrics


def test_calculate_metrics_basic():
    y_true = np.array([0, 1, 0, 1, 0])
    y_pred = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

    metrics = calculate_metrics(y_true, y_pred)

    assert set(metrics.keys()) == {"logloss", "AUC", "calibration"}
    assert_almost_equal(metrics["logloss"], 0.736, decimal=3)
    assert_almost_equal(metrics["AUC"], 0.5, decimal=1)
    assert_almost_equal(metrics["calibration"], 0.75, decimal=2)
