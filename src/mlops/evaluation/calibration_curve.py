import matplotlib.pyplot as plt
import numpy.typing as npt
from matplotlib.figure import Figure
from sklearn.calibration import calibration_curve


def plot_calibration_curve(y_true: npt.NDArray, y_pred: npt.NDArray, n_bins: int = 50) -> Figure:
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=n_bins)

    fig = plt.figure(figsize=(6, 6))

    plt.plot([0, 0.5], [0, 0.5], "k:", label="Ideal")
    plt.plot(prob_pred, prob_true, "s-", label="Model")

    plt.xlabel("Mean predicted probability")
    plt.ylabel("Fraction of positives")
    plt.title("Calibration Curve")
    plt.xlim(0, 0.5)
    plt.ylim(0, 0.5)
    plt.legend(loc="best")

    plt.tight_layout()

    return fig
