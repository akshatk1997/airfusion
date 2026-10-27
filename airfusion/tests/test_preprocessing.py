"""
Tests for preprocessing module: missing values, bounds, interpolation.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.preprocessing import clean_air_quality_dataframe, detect_outliers_iqr


def test_clean_air_quality_dataframe_imputation():
    timestamps = pd.date_range("2026-01-01", periods=10, freq="h")
    # Insert NaN in the middle
    pm25_vals = [20.0, 22.0, np.nan, np.nan, 28.0, 30.0, 32.0, 35.0, 40.0, 45.0]
    temps = [15.0, 16.0, 17.0, np.nan, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0]

    df = pd.DataFrame({
        "timestamp": timestamps,
        "pm2_5": pm25_vals,
        "temperature": temps
    })

    cleaned = clean_air_quality_dataframe(df)

    assert cleaned["pm2_5"].isna().sum() == 0
    assert cleaned["temperature"].isna().sum() == 0
    # Interpolation should linearly fill between 22 and 28
    assert 22.0 < cleaned.loc[2, "pm2_5"] < 28.0


def test_clean_air_quality_dataframe_bounds():
    timestamps = pd.date_range("2026-01-01", periods=5, freq="h")
    # Negative pm2_5 and extreme temperature
    df = pd.DataFrame({
        "timestamp": timestamps,
        "pm2_5": [-50.0, 25.0, 30.0, 35.0, 40.0],
        "temperature": [20.0, 21.0, 150.0, 22.0, 23.0]
    })

    cleaned = clean_air_quality_dataframe(df)

    assert (cleaned["pm2_5"] >= 0.0).all()
    assert (cleaned["temperature"] <= 60.0).all()


def test_detect_outliers_iqr():
    s = pd.Series([10.0, 12.0, 11.0, 13.0, 12.5, 11.8, 500.0])
    outliers = detect_outliers_iqr(s, multiplier=2.5)
    assert outliers.iloc[-1] == True
    assert outliers.iloc[0] == False
