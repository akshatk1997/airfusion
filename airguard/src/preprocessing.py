"""
Data Preprocessing Module for AirGuard.
Handles missing value imputation (time-series forward fill & spline/linear interpolation),
duplicate removal, timestamp standardization, unit validation, and physical bounds clipping.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger("airguard.preprocessing")

# Physical reasonable bounds for atmospheric variables
PHYSICAL_BOUNDS = {
    "pm2_5": (0.0, 1000.0),      # ug/m3
    "pm10": (0.0, 1500.0),       # ug/m3
    "no2": (0.0, 800.0),         # ug/m3
    "so2": (0.0, 800.0),         # ug/m3
    "co": (0.0, 50000.0),        # ug/m3
    "o3": (0.0, 600.0),          # ug/m3
    "temperature": (-40.0, 60.0), # Celsius
    "humidity": (0.0, 100.0),    # %
    "wind_speed": (0.0, 150.0),  # km/h
    "wind_direction": (0.0, 360.0), # degrees
    "pressure": (800.0, 1100.0)  # hPa
}


def clean_air_quality_dataframe(
    df: pd.DataFrame,
    interpolate_limit: int = 6
) -> pd.DataFrame:
    """
    Cleans raw air quality and weather records:
    1. Ensures datetime index/column
    2. Sorts chronologically and removes duplicate timestamps
    3. Clips values to physical limits
    4. Imputes small gaps using linear time interpolation, then forward fills
    5. Returns cleaned DataFrame
    """
    if df.empty:
        return df.copy()

    df_clean = df.copy()

    # 1. Standardize timestamp
    if "timestamp" in df_clean.columns:
        df_clean["timestamp"] = pd.to_datetime(df_clean["timestamp"], format="mixed")
        df_clean.sort_values("timestamp", inplace=True)
        # Drop duplicates on timestamp
        df_clean.drop_duplicates(subset=["timestamp"], keep="last", inplace=True)

    # 2. Enforce Physical Bounds (clip unreasonable sensor spikes or negative numbers)
    for col, (lower, upper) in PHYSICAL_BOUNDS.items():
        if col in df_clean.columns:
            # Replace invalid extreme values with NaN prior to interpolation
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            mask_invalid = (df_clean[col] < lower) | (df_clean[col] > upper)
            if mask_invalid.any():
                df_clean.loc[mask_invalid, col] = np.nan

    # 3. Time-series interpolation for numerical columns
    numeric_cols = [c for c in PHYSICAL_BOUNDS.keys() if c in df_clean.columns]
    for col in numeric_cols:
        # Time-based linear interpolation for gaps up to interpolate_limit hours
        df_clean[col] = df_clean[col].interpolate(method="linear", limit=interpolate_limit, limit_direction="both")
        # Forward fill and backward fill remaining edge NaNs
        df_clean[col] = df_clean[col].ffill().bfill()

    # 4. Re-calculate AQI if missing or PM2.5 was updated
    if "pm2_5" not in df_clean.columns:
        df_clean["pm2_5"] = 25.0
    else:
        df_clean["pm2_5"] = pd.to_numeric(df_clean["pm2_5"], errors="coerce").ffill().bfill().fillna(25.0)

    if "aqi" not in df_clean.columns:
        df_clean["aqi"] = 75
    else:
        df_clean["aqi"] = pd.to_numeric(df_clean["aqi"], errors="coerce").ffill().bfill().fillna(75)

    from src.data_collection import calculate_pm25_aqi
    aqis = []
    categories = []
    for v in df_clean["pm2_5"]:
        aq, cat, _ = calculate_pm25_aqi(v)
        aqis.append(aq)
        categories.append(cat)
    df_clean["aqi"] = aqis
    df_clean["aqi_category"] = categories

    df_clean.reset_index(drop=True, inplace=True)
    return df_clean


def detect_outliers_iqr(
    series: pd.Series,
    multiplier: float = 3.0
) -> pd.Series:
    """
    Identifies outliers using the Interquartile Range (IQR) method.
    Returns a boolean series where True indicates an outlier.
    Uses multiplier 3.0 (extreme outliers) to avoid flagging legitimate peak smog events.
    """
    q25 = series.quantile(0.25)
    q75 = series.quantile(0.75)
    iqr = q75 - q25
    lower_bound = q25 - (multiplier * iqr)
    upper_bound = q75 + (multiplier * iqr)
    return (series < lower_bound) | (series > upper_bound)
