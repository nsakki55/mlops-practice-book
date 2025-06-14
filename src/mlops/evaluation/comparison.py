import logging

import numpy.typing as npt
from sklearn.metrics import log_loss

from .metrics import calibration_score

logger = logging.getLogger(__name__)


def is_model_better_than_baseline(
    y_pred: npt.NDArray,
    y_baseline: npt.NDArray,
    y_true: npt.NDArray,
) -> bool:
    return (
        _is_better_logloss(y_pred=y_pred, y_baseline=y_baseline, y_true=y_true)  # noqa
        and _is_better_calibration(y_pred=y_pred, y_baseline=y_baseline, y_true=y_true)
    )


def _is_better_logloss(y_pred: npt.NDArray, y_baseline: npt.NDArray, y_true: npt.NDArray) -> bool:
    logloss = log_loss(y_true=y_true, y_pred=y_pred)
    logloss_baseline = log_loss(y_true=y_true, y_pred=y_baseline)
    logger.info(f"logloss: {logloss}, baseline: {logloss_baseline}")
    return logloss <= logloss_baseline


def _is_better_calibration(y_pred: npt.NDArray, y_baseline: npt.NDArray, y_true: npt.NDArray) -> bool:
    calibration = calibration_score(y_true=y_true, y_pred=y_pred)
    calibration_baseline = calibration_score(y_true=y_true, y_pred=y_baseline)
    logger.info(f"calibration: {calibration}, baseline: {calibration_baseline}")
    return abs(calibration - 1) <= abs(calibration_baseline - 1)
