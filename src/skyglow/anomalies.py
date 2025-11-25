import pandas as pd
import numpy as np

def detect_anomalies(
    ts: pd.Series,
    window: int = 12,
    z_thresh: float = 2.5
) -> pd.DataFrame:
    """
    ts: monthly mean radiance (indexed by date)
    window: rolling window in months for baseline
    """
    df = pd.DataFrame({"mean_radiance": ts})

    # Rolling mean/std as baseline
    df["roll_mean"] = df["mean_radiance"].rolling(window, min_periods=6).mean()
    df["roll_std"] = df["mean_radiance"].rolling(window, min_periods=6).std()

    # Z-score relative to rolling baseline (to be expanded in future updates)
    df["z_score"] = (df["mean_radiance"] - df["roll_mean"]) / df["roll_std"]
    df["is_anomaly"] = df["z_score"].abs() > z_thresh

    return df


