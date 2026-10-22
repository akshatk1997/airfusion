"""
Prediction & Forecasting Module for AirGuard.
Loads trained ML models, generates 24-hour and 72-hour multi-step PM2.5 forecasts
with uncertainty confidence bands, and saves forecast records to SQLite.
"""

from __future__ import annotations

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Add project root to sys.path
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
import numpy as np
import pandas as pd

from src.config import (
    BEST_MODEL_PATH,
    SCALER_PATH,
    FEATURE_NAMES_PATH,
    TARGET_VARIABLE,
    DB_PATH
)
from src.database import (
    fetch_historical_records,
    get_or_create_location,
    insert_forecast_records
)
from src.data_collection import (
    fetch_and_store_city_data,
    calculate_pm25_aqi,
    geocode_city
)
from src.preprocessing import clean_air_quality_dataframe
from src.feature_engineering import build_feature_pipeline

logger = logging.getLogger("airguard.predict")


def is_model_trained(model_path: Optional[Path | str] = None) -> bool:
    """
    Check if the trained model artifact exists on disk.
    """
    path = Path(model_path or BEST_MODEL_PATH)
    return path.exists() and path.is_file()


def load_model_bundle(model_path: Optional[Path | str] = None) -> Optional[Dict[str, Any]]:
    """
    Load serialized model bundle from disk.
    """
    path = Path(model_path or BEST_MODEL_PATH)
    if not path.exists():
        logger.warning(f"Model file {path} not found. Please train models first.")
        return None
    try:
        bundle = joblib.load(path)
        return bundle
    except Exception as e:
        logger.error(f"Error loading model bundle: {e}")
        return None


def generate_forecast(
    city_name: str,
    horizon_hours: int = 72,
    db_path: Optional[Path | str] = None
) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
    """
    Generate an hourly PM2.5 and AQI forecast for up to `horizon_hours` (e.g. 24 or 72).
    Returns (forecast_dataframe, summary_metrics).
    """
    bundle = load_model_bundle()
    if not bundle:
        return None, {"error": "Model not trained yet."}

    # Fetch fresh city data
    loc_meta, recent_df = fetch_and_store_city_data(city_name, past_days=7, forecast_days=4)
    if recent_df.empty or not loc_meta:
        # Fallback to local DB records
        loc_meta = geocode_city(city_name)
        if not loc_meta:
            return None, {"error": f"City '{city_name}' could not be resolved."}
        recent_df = fetch_historical_records(city=loc_meta["city"], db_path=db_path)

    if recent_df.empty or len(recent_df) < 24:
        return None, {"error": f"Insufficient historical data available for {city_name}."}

    cleaned_df = clean_air_quality_dataframe(recent_df)
    featured_df, feature_cols, _ = build_feature_pipeline(cleaned_df, horizons=[24, 72])

    required_features = bundle.get("feature_names", feature_cols)
    # Ensure all required features are present
    for col in required_features:
        if col not in featured_df.columns:
            featured_df[col] = 0.0

    # Get the latest observation row as base
    latest_row = featured_df.iloc[-1:].copy()
    base_time = pd.to_datetime(latest_row["timestamp"].values[0], format="mixed")
    current_pm25 = float(latest_row["pm2_5"].values[0])

    model_1h = bundle.get("model_1h")
    model_24h = bundle.get("model_24h")
    model_72h = bundle.get("model_72h")
    best_name = bundle.get("best_model_name", "XGBoost")

    # Generate sequential hourly trajectory
    forecast_rows = []
    running_pm25 = current_pm25
    running_features = latest_row[required_features].copy()

    # Estimate standard error for uncertainty bands (~12% to 25% expanding over horizon)
    base_std_err = max(3.5, current_pm25 * 0.10)

    for h in range(1, horizon_hours + 1):
        target_time = base_time + timedelta(hours=h)

        # Update cyclical time features for horizon step h
        hour = target_time.hour
        dayofweek = target_time.dayofweek
        month = target_time.month

        if "hour_sin" in running_features.columns:
            running_features["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
            running_features["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)
            running_features["dayofweek_sin"] = np.sin(2 * np.pi * dayofweek / 7.0)
            running_features["dayofweek_cos"] = np.cos(2 * np.pi * dayofweek / 7.0)
            running_features["month_sin"] = np.sin(2 * np.pi * (month - 1) / 12.0)
            running_features["month_cos"] = np.cos(2 * np.pi * (month - 1) / 12.0)
            running_features["is_weekend"] = int(dayofweek in [5, 6])

        # Step prediction
        X_step = running_features[required_features].values
        if h == 24 and model_24h is not None:
            pred_step = float(model_24h.predict(X_step)[0])
        elif h == 72 and model_72h is not None:
            pred_step = float(model_72h.predict(X_step)[0])
        elif model_1h is not None:
            pred_step = float(model_1h.predict(X_step)[0])
        elif model_24h is not None:
            pred_step = float(model_24h.predict(X_step)[0])
        else:
            pred_step = running_pm25

        # Clip physically
        pred_pm25 = max(1.0, round(float(pred_step), 2))

        # Dynamic uncertainty band: expands with horizon sqrt(h)
        uncertainty = base_std_err * np.sqrt(1.0 + (h / 12.0))
        lower_ci = max(0.5, round(pred_pm25 - (1.645 * uncertainty), 2))
        upper_ci = round(pred_pm25 + (1.645 * uncertainty), 2)

        pred_aqi, pred_category, pred_color = calculate_pm25_aqi(pred_pm25)

        forecast_rows.append({
            "location_id": loc_meta.get("location_id", 1),
            "forecast_time": base_time.isoformat(),
            "target_time": target_time.strftime("%Y-%m-%d %H:%M"),
            "horizon_hours": h,
            "predicted_pm2_5": pred_pm25,
            "predicted_aqi": pred_aqi,
            "predicted_category": pred_category,
            "predicted_color": pred_color,
            "lower_ci": lower_ci,
            "upper_ci": upper_ci,
            "model_name": best_name
        })

        # Autoregressive update for next hour
        running_pm25 = pred_pm25
        if f"{TARGET_VARIABLE}_lag_1h" in running_features.columns:
            running_features[f"{TARGET_VARIABLE}_lag_1h"] = running_pm25
        if TARGET_VARIABLE in running_features.columns:
            running_features[TARGET_VARIABLE] = running_pm25

    forecast_df = pd.DataFrame(forecast_rows)

    # Save forecasts to SQLite database
    try:
        insert_forecast_records(forecast_rows, db_path=db_path)
    except Exception as e:
        logger.warning(f"Could not persist forecast records to DB: {e}")

    # Summary metrics
    val_24h = forecast_df[forecast_df["horizon_hours"] == min(24, horizon_hours)].iloc[0]
    val_72h = forecast_df[forecast_df["horizon_hours"] == min(72, horizon_hours)].iloc[0] if horizon_hours >= 72 else None

    summary = {
        "city": loc_meta["city"],
        "base_timestamp": base_time.strftime("%Y-%m-%d %H:%M"),
        "current_pm2_5": current_pm25,
        "current_aqi": calculate_pm25_aqi(current_pm25)[0],
        "forecast_24h_pm2_5": val_24h["predicted_pm2_5"],
        "forecast_24h_aqi": val_24h["predicted_aqi"],
        "forecast_24h_category": val_24h["predicted_category"],
        "forecast_72h_pm2_5": val_72h["predicted_pm2_5"] if val_72h is not None else None,
        "forecast_72h_aqi": val_72h["predicted_aqi"] if val_72h is not None else None,
        "forecast_72h_category": val_72h["predicted_category"] if val_72h is not None else None,
        "model_used": best_name
    }

    return forecast_df, summary
