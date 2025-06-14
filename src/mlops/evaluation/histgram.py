import matplotlib.pyplot as plt
import numpy.typing as npt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure


def plot_histgram(y_true: npt.NDArray, y_pred: npt.NDArray) -> Figure:
    fig = plt.figure(figsize=(10, 6))
    df_hist = pd.DataFrame({"y_pred": y_pred, "y_true": y_true})
    sns.histplot(data=df_hist, x="y_pred", hue="y_true", bins=100)
    plt.title("Distribution of prediction value")

    return fig
