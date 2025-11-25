# tests/test_anomalies.py

import pandas as pd

from src.skyglow.anomalies import detect_anomalies


def test_detect_anomalies_basic():
    # Simple series with one clear spike
    dates = pd.date_range("2020-01-01", periods=12, freq="MS")
    values = [1, 1, 1, 1, 10, 1, 1, 1, 1, 1, 1, 1]
    ts = pd.Series(values, index=dates)

    df = detect_anomalies(ts, window=3, z_thresh=2.0)

    # The big spike should be flagged
    assert df.loc["2020-05-01", "is_anomaly"]

    # Some of the non-spike points should not be anomalies
    assert not df.loc["2020-02-01", "is_anomaly"]

