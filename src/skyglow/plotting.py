import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def plot_timeseries_with_anomalies(df: pd.DataFrame, out_path: Path):
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(df.index, df["mean_radiance"], label="Mean radiance")
    # Highlight anomalies
    anomalies = df[df["is_anomaly"]]
    ax.scatter(anomalies.index, anomalies["mean_radiance"], marker="o", label="Anomaly")

    ax.set_ylabel("Mean radiance (nW/cm²/sr)")
    ax.set_xlabel("Date")
    ax.legend()
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)

