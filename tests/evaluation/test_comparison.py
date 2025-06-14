import numpy as np

from mlops.evaluation import is_model_better_than_baseline


def test_is_model_better_than_baseline_when_true():
    y_true = np.array([0, 1, 1, 0, 1])
    y_pred = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
    y_baseline = np.array([0.3, 0.6, 0.6, 0.4, 0.6])

    result_better = is_model_better_than_baseline(y_pred=y_pred, y_baseline=y_baseline, y_true=y_true)
    assert result_better

    result_same = is_model_better_than_baseline(y_pred=y_baseline, y_baseline=y_baseline, y_true=y_true)
    assert result_same


def test_is_model_better_than_baseline_when_false():
    y_true = np.array([0, 1, 1, 0, 1])
    y_baseline = np.array([0.3, 0.6, 0.6, 0.4, 0.6])
    y_pred = np.array([0.5, 0.5, 0.5, 0.5, 0.5])

    result_worse = is_model_better_than_baseline(y_pred=y_pred, y_baseline=y_baseline, y_true=y_true)
    assert not result_worse
