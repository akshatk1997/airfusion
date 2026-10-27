"""
Explainability & Interpretability Module for AirFusion.
Provides global feature importance, SHAP-based tree explanations,
and natural language diagnostic insights explaining forecast drivers.
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import shap

from src.predict import load_model_bundle

logger = logging.getLogger("airfusion.explainability")


def get_global_feature_importance(top_n: int = 15) -> pd.DataFrame:
    """
    Extracts normalized global feature importances from the trained champion model.
    """
    bundle = load_model_bundle()
    if not bundle:
        return pd.DataFrame(columns=["feature", "importance"])

    model = bundle.get("model_24h")
    feature_names = bundle.get("feature_names", [])

    if model is None or not feature_names:
        return pd.DataFrame(columns=["feature", "importance"])

    importances = None
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_)

    if importances is None or len(importances) != len(feature_names):
        return pd.DataFrame(columns=["feature", "importance"])

    df_imp = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    })

    # Normalize to percentage
    total = df_imp["importance"].sum()
    if total > 0:
        df_imp["importance"] = (df_imp["importance"] / total) * 100.0

    # Human-friendly feature labels
    label_map = {
        "pm2_5": "Current PM2.5 Level",
        "pm2_5_lag_1h": "PM2.5 (1 Hour Ago)",
        "pm2_5_lag_3h": "PM2.5 (3 Hours Ago)",
        "pm2_5_lag_6h": "PM2.5 (6 Hours Ago)",
        "pm2_5_lag_12h": "PM2.5 (12 Hours Ago)",
        "pm2_5_lag_24h": "PM2.5 (Previous Day Same Hour)",
        "pm2_5_lag_48h": "PM2.5 (48 Hours Ago)",
        "pm2_5_roll_mean_6h": "6h Rolling Average PM2.5",
        "pm2_5_roll_mean_12h": "12h Rolling Average PM2.5",
        "pm2_5_roll_mean_24h": "24h Rolling Average PM2.5",
        "pm2_5_roll_std_6h": "6h PM2.5 Volatility",
        "pm2_5_roll_std_24h": "24h PM2.5 Volatility",
        "pm2_5_roll_max_24h": "24h Peak PM2.5",
        "pm2_5_roll_min_24h": "24h Minimum PM2.5",
        "wind_speed": "Wind Speed (km/h)",
        "wind_speed_lag_1h": "Wind Speed (1h Prior)",
        "wind_stagnation_index": "Atmospheric Stagnation",
        "wind_humidity_dispersion": "Wind-Humidity Dispersion",
        "temperature": "Ambient Temperature (°C)",
        "temperature_lag_24h": "Temperature (Previous Day)",
        "humidity": "Relative Humidity (%)",
        "humidity_lag_1h": "Humidity (1h Prior)",
        "pressure": "Atmospheric Pressure (hPa)",
        "pm10": "Coarse Particulates (PM10)",
        "pm25_pm10_ratio": "PM2.5/PM10 Combustion Ratio",
        "no2": "Nitrogen Dioxide (NO2)",
        "so2": "Sulphur Dioxide (SO2)",
        "co": "Carbon Monoxide (CO)",
        "o3": "Ozone (O3)",
        "hour_sin": "Hour of Day (Diurnal Cycle)",
        "hour_cos": "Hour of Day (Diurnal Phase)",
        "dayofweek_sin": "Day of Week Pattern",
        "is_weekend": "Weekend / Traffic Reduction Factor"
    }

    df_imp["display_name"] = df_imp["feature"].map(lambda x: label_map.get(x, x.replace("_", " ").title()))
    df_imp.sort_values("importance", ascending=False, inplace=True)
    df_imp.reset_index(drop=True, inplace=True)

    return df_imp.head(top_n)


def compute_shap_explanations(
    sample_df: pd.DataFrame,
    max_samples: int = 50
) -> Tuple[Optional[np.ndarray], Optional[List[str]]]:
    """
    Computes SHAP values using TreeExplainer for tree models.
    """
    bundle = load_model_bundle()
    if not bundle:
        return None, None

    model = bundle.get("model_24h")
    feature_names = bundle.get("feature_names", [])

    if model is None or not hasattr(model, "predict"):
        return None, None

    # Filter available features
    cols = [c for c in feature_names if c in sample_df.columns]
    X_sample = sample_df[cols].dropna().head(max_samples)
    if X_sample.empty:
        return None, None

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        return shap_values, cols
    except Exception as e:
        logger.warning(f"Could not compute SHAP values directly: {e}")
        return None, None


def generate_natural_language_insight(
    city: str,
    current_pm25: float,
    forecast_24h_pm25: float,
    weather_info: Optional[Dict[str, Any]] = None
) -> str:
    """
    Synthesizes model predictions, weather conditions, and diurnal factors
    into a human-readable diagnostic insight.
    """
    if weather_info is None:
        weather_info = {}

    wind_speed = weather_info.get("wind_speed", 5.0)
    humidity = weather_info.get("humidity", 50.0)
    temperature = weather_info.get("temperature", 25.0)

    delta = forecast_24h_pm25 - current_pm25
    direction = "rise" if delta > 5 else ("drop" if delta < -5 else "remain stable")
    pct_change = abs(round((delta / max(current_pm25, 1.0)) * 100.0, 1))

    # Identify primary meteorological driving factors
    drivers = []
    if wind_speed is not None and wind_speed < 4.0:
        drivers.append(f"low wind speed ({wind_speed:.1f} km/h) causing particulate stagnation")
    elif wind_speed is not None and wind_speed > 12.0:
        drivers.append(f"strong atmospheric ventilation ({wind_speed:.1f} km/h wind) aiding dispersion")

    if humidity is not None and humidity > 70.0:
        drivers.append(f"high relative humidity ({humidity:.0f}%) promoting secondary aerosol condensation")
    elif humidity is not None and humidity < 35.0:
        drivers.append(f"dry air conditions ({humidity:.0f}% humidity)")

    if current_pm25 > 60.0:
        drivers.append(f"elevated baseline particulate load ({current_pm25:.1f} µg/m³)")
    elif current_pm25 < 25.0:
        drivers.append(f"clean initial ambient conditions ({current_pm25:.1f} µg/m³)")

    if not drivers:
        drivers.append("seasonal diurnal cycles and local emissions")

    drivers_sentence = ", ".join(drivers)

    if direction == "remain stable":
        insight = (
            f"**{city} Air Quality Outlook**: PM2.5 levels are projected to **remain steady** over the next 24 hours "
            f"(~{forecast_24h_pm25:.1f} µg/m³ vs current {current_pm25:.1f} µg/m³), balanced by {drivers_sentence}."
        )
    elif direction == "rise":
        insight = (
            f"**{city} Air Quality Outlook**: PM2.5 is projected to **increase by {pct_change}%** over the next 24 hours "
            f"(reaching ~{forecast_24h_pm25:.1f} µg/m³), driven primarily by **{drivers_sentence}**."
        )
    else:
        insight = (
            f"**{city} Air Quality Outlook**: PM2.5 is projected to **improve by {pct_change}%** over the next 24 hours "
            f"(dropping to ~{forecast_24h_pm25:.1f} µg/m³), assisted by **{drivers_sentence}**."
        )

    return insight
