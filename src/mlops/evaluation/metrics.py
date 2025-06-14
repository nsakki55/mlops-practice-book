import logging

import numpy.typing as npt
from sklearn.metrics import log_loss, roc_auc_score

logger = logging.getLogger(__name__)


def calculate_metrics(y_true: npt.NDArray, y_pred: npt.NDArray) -> dict[str, float]:
    logloss = log_loss(y_true=y_true, y_pred=y_pred)
    roc_auc = roc_auc_score(y_true=y_true, y_score=y_pred)
    calibration = calibration_score(y_true=y_true, y_pred=y_pred)
    logger.info(f"logloss: {logloss}, AUC: {roc_auc}, calibration: {calibration}")
    return {
        "logloss": logloss,
        "AUC": roc_auc,
        "calibration": calibration,
    }


def calibration_score(y_true: npt.NDArray, y_pred: npt.NDArray) -> float:
    return sum(y_pred) / sum(y_true)
