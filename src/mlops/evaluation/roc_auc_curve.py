import matplotlib.pyplot as plt
import numpy.typing as npt
from matplotlib.figure import Figure
from sklearn.metrics import roc_curve


def plot_roc_auc_curve(y_true: npt.NDArray, y_pred: npt.NDArray) -> Figure:
    [fpr, tpr, _] = roc_curve(y_true, y_pred)

    fig = plt.figure(figsize=(6, 6))
    plt.plot(fpr, tpr, label="Model")
    plt.plot([0, 1], [0, 1], "k--", label="Random")
    plt.xlabel("False Positive Rate (specificity)")
    plt.ylabel("True Positive Rate (recall)")
    plt.title("ROC Curve")
    plt.legend()

    return fig
