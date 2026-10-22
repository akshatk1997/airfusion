"""
Tests for feature engineering: lags, rolling windows, cyclical features, time split.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.feature_engineering import (
    create_time_features,
    create_lag_features,
    create_rolling_features,
    create_interaction_features,
    build_feature_pipeline,
    time_series_split
)


def test_create_time_features():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-06-01 00:00:00", periods=24, freq="h")
    })
    featured = create_time_features(df)
    assert "hour_sin" in featured.columns
    assert "hour_cos" in featured.columns
    assert "dayofweek_sin" in featured.columns
    assert "is_weekend" in featured.columns

    # Hour 0 should have hour_sin = 0, hour_cos = 1
    assert abs(featured.loc[0, "hour_sin"]) < 1e-4
    assert abs(featured.loc[0, "hour_cos"] - 1.0) < 1e-4


def test_create_lag_features():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=10, freq="h"),
        "pm2_5": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    })
    lagged = create_lag_features(df, target_col="pm2_5", lags=[1, 3])
    assert "pm2_5_lag_1h" in lagged.columns
    assert "pm2_5_lag_3h" in lagged.columns
    assert pd.isna(lagged.loc[0, "pm2_5_lag_1h"])
    assert lagged.loc[1, "pm2_5_lag_1h"] == 10.0
    assert lagged.loc[3, "pm2_5_lag_3h"] == 10.0


def test_build_feature_pipeline():
    n = 100
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=n, freq="h"),
        "pm2_5": np.random.uniform(10, 80, n),
        "pm10": np.random.uniform(20, 150, n),
        "temperature": np.random.uniform(15, 35, n),
        "humidity": np.random.uniform(30, 90, n),
        "wind_speed": np.random.uniform(1, 15, n)
    })
    data, feature_cols, target_cols = build_feature_pipeline(df, horizons=[24, 72])
    assert "target_lead_24h" in target_cols
    assert "target_lead_72h" in target_cols
    assert len(feature_cols) > 10
    # Ensure targets are not in feature_cols (no leakage!)
    for t in target_cols:
        assert t not in feature_cols


def test_time_series_split():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=100, freq="h"),
        "val": range(100)
    })
    train, val, test = time_series_split(df, 0.7, 0.15, 0.15)
    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15
    # Strict order
    assert train["val"].max() < val["val"].min()
    assert val["val"].max() < test["val"].min()
