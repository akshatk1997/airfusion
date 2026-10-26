"""
Feature Engineering Module for AirGuard.
Constructs time-series lag features, rolling statistics, cyclical diurnal/seasonal
transforms, atmospheric stagnation indicators, and multi-horizon target variables.
"""

from __future__ import annotations

import logging
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd

from src.config import LAG_HOURS, ROLLING_WINDOWS, TARGET_VARIABLE

logger = logging.getLogger("airguard.feature_engineering")


def create_time_features(df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DataFrame:
    """
    Extract diurnal, weekly, and seasonal cyclical features from timestamps.
    Transforms linear hour/day/month into sin/cos continuous manifolds.
    """
    data = df.copy()
    if timestamp_col not in data.columns:
        raise ValueError(f"Timestamp column '{timestamp_col}' not found in DataFrame.")

    dt = pd.to_datetime(data[timestamp_col], format="mixed")

    # Linear calendar components
    hour = dt.dt.hour
    dayofweek = dt.dt.dayofweek
    month = dt.dt.month

    # Cyclical sin/cos encodings
    data["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
    data["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)
    data["dayofweek_sin"] = np.sin(2 * np.pi * dayofweek / 7.0)
    data["dayofweek_cos"] = np.cos(2 * np.pi * dayofweek / 7.0)
    data["month_sin"] = np.sin(2 * np.pi * (month - 1) / 12.0)
    data["month_cos"] = np.cos(2 * np.pi * (month - 1) / 12.0)

    # Weekend binary indicator (Saturday=5, Sunday=6)
    data["is_weekend"] = dayofweek.isin([5, 6]).astype(int)

    return data


def create_lag_features(
    df: pd.DataFrame,
    target_col: str = TARGET_VARIABLE,
    lags: Optional[List[int]] = None
) -> pd.DataFrame:
    """
    Creates historical autoregressive lag features for the target pollutant.
    """
    data = df.copy()
    if target_col not in data.columns:
        data[target_col] = 25.0
    if lags is None:
        lags = LAG_HOURS

    for lag in lags:
        data[f"{target_col}_lag_{lag}h"] = data[target_col].shift(lag)

    # Weather lags (temperature and wind speed previous hours)
    if "wind_speed" in data.columns:
        data["wind_speed_lag_1h"] = data["wind_speed"].shift(1)
        data["wind_speed_lag_3h"] = data["wind_speed"].shift(3)
    if "temperature" in data.columns:
        data["temperature_lag_1h"] = data["temperature"].shift(1)
        data["temperature_lag_24h"] = data["temperature"].shift(24)
    if "humidity" in data.columns:
        data["humidity_lag_1h"] = data["humidity"].shift(1)

    return data


def create_rolling_features(
    df: pd.DataFrame,
    target_col: str = TARGET_VARIABLE,
    windows: Optional[List[int]] = None
) -> pd.DataFrame:
    """
    Computes rolling mean, standard deviation, min, and max over specified hourly windows.
    Uses closed='left' by shifting by 1 to prevent data leakage from the current timestamp.
    """
    data = df.copy()
    if target_col not in data.columns:
        data[target_col] = 25.0
    if windows is None:
        windows = ROLLING_WINDOWS

    # Shift by 1 hour so the rolling stats only use past information up to t-1
    shifted = data[target_col].shift(1)

    for w in windows:
        data[f"{target_col}_roll_mean_{w}h"] = shifted.rolling(window=w, min_periods=1).mean()
        data[f"{target_col}_roll_std_{w}h"] = shifted.rolling(window=w, min_periods=1).std().fillna(0.0)
        data[f"{target_col}_roll_min_{w}h"] = shifted.rolling(window=w, min_periods=1).min()
        data[f"{target_col}_roll_max_{w}h"] = shifted.rolling(window=w, min_periods=1).max()

    return data


def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derives meteorological & atmospheric interaction features:
    - Inverted wind speed: stagnation factor (low wind retains particulates)
    - PM2.5 / PM10 ratio: characterizes combustion/fine aerosol vs mechanical dust
    - Temperature-Humidity Index / Dew point proxy
    """
    data = df.copy()

    # Atmospheric Stagnation: Wind dispersion proxy
    if "wind_speed" in data.columns:
        data["wind_stagnation_index"] = 1.0 / (data["wind_speed"].clip(lower=0.5))

    # Aerosol Fraction (PM2.5 to PM10 ratio)
    if "pm2_5" in data.columns and "pm10" in data.columns:
        pm10_safe = data["pm10"].replace(0, np.nan)
        data["pm25_pm10_ratio"] = (data["pm2_5"] / pm10_safe).clip(0.0, 1.5).fillna(0.5)

    # Weather Interaction: Wind * Humidity dispersion
    if "wind_speed" in data.columns and "humidity" in data.columns:
        data["wind_humidity_dispersion"] = data["wind_speed"] * (100.0 - data["humidity"]) / 100.0

    return data


def build_feature_pipeline(
    df: pd.DataFrame,
    target_col: str = TARGET_VARIABLE,
    horizons: Optional[List[int]] = None
) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    End-to-end feature engineering pipeline:
    1. Generates time features
    2. Generates lag features
    3. Generates rolling window statistics
    4. Generates atmospheric interactions
    5. Creates future lead targets for horizons (e.g. 24h and 72h ahead)
    Returns: (featured_df, feature_columns, target_columns)
    """
    if horizons is None:
        horizons = [24, 72]

    if target_col not in df.columns:
        df = df.copy()
        df[target_col] = 25.0

    # Apply transformations
    data = create_time_features(df)
    data = create_lag_features(data, target_col=target_col)
    data = create_rolling_features(data, target_col=target_col)
    data = create_interaction_features(data)

    target_cols = []
    # Create multi-horizon targets
    for h in horizons:
        col_name = f"target_lead_{h}h"
        data[col_name] = data[target_col].shift(-h)
        target_cols.append(col_name)

    # Single-step lead target for continuous 1h step forecasting
    data["target_lead_1h"] = data[target_col].shift(-1)
    target_cols.append("target_lead_1h")

    # Determine predictor feature columns (exclude targets, metadata, future data)
    exclude_cols = set(target_cols + [
        "timestamp", "aqi_category", "raw_json", "source", "city",
        "state", "country", "location_id", "id", "created_at"
    ])

    feature_cols = [c for c in data.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(data[c])]

    return data, feature_cols, target_cols


def time_series_split(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits time series sequentially without random shuffling.
    Preserves strict chronological order.
    """
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()

    logger.info(f"Split sizes: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
    return train_df, val_df, test_df
