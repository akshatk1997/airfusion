"""
Alerts & Health Advisory Module for AirFusion.
Evaluates user thresholds against real-time and forecasted readings,
logs triggered incidents, and provides health guidance and preventive recommendations.
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd

from src.config import AQI_CATEGORIES, HIGH_POLLUTION_PM25_THRESHOLD
from src.database import fetch_alerts, log_alert_trigger

logger = logging.getLogger("airfusion.alerts")


def get_health_advisory(aqi: int) -> Dict[str, Any]:
    """
    Returns structured health guidance, warning level, color, and precautions
    corresponding to a specific AQI level.
    """
    for cat in AQI_CATEGORIES:
        if cat["aqi_min"] <= aqi <= cat["aqi_max"]:
            return {
                "category": cat["category"],
                "color": cat["color"],
                "description": cat["description"],
                "advice": cat["advice"]
            }

    # If > 500
    if aqi > 500:
        hazardous = AQI_CATEGORIES[-1]
        return {
            "category": hazardous["category"],
            "color": hazardous["color"],
            "description": hazardous["description"],
            "advice": hazardous["advice"]
        }

    return {
        "category": "Unknown",
        "color": "#808080",
        "description": "AQI level not available.",
        "advice": {
            "general": "Monitor local conditions.",
            "exercise": "Take standard precautions.",
            "mask": "Optional.",
            "ventilation": "Standard ventilation.",
            "sensitive": "Consult physician if feeling unwell."
        }
    }


def evaluate_alerts_for_city(
    city: str,
    current_pm25: float,
    current_aqi: int,
    forecast_df: Optional[pd.DataFrame] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates all active alerts configured for a city or globally.
    Checks both current readings and upcoming forecast horizons.
    Logs any triggered breaches into the alert_logs table.
    """
    alerts = fetch_alerts(active_only=True)
    city_alerts = [
        a for a in alerts
        if a["city"].lower() in [city.lower(), "all", "global"]
    ]

    # Default safety alerts if none configured
    if not city_alerts:
        city_alerts = [
            {"id": 0, "city": city, "metric": "pm2_5", "threshold_value": HIGH_POLLUTION_PM25_THRESHOLD, "condition": "greater_than"},
            {"id": -1, "city": city, "metric": "aqi", "threshold_value": 150.0, "condition": "greater_than"}
        ]

    triggered: List[Dict[str, Any]] = []

    for alert in city_alerts:
        metric = alert.get("metric", "pm2_5")
        threshold = float(alert.get("threshold_value", 55.5))
        alert_id = alert.get("id")

        current_val = current_pm25 if metric == "pm2_5" else current_aqi
        metric_label = "PM2.5" if metric == "pm2_5" else "AQI"
        unit = "µg/m³" if metric == "pm2_5" else "index"

        # 1. Check Current Level
        if current_val >= threshold:
            msg = (
                f"CURRENT BREACH: {city} {metric_label} is {current_val:.1f} {unit}, "
                f"exceeding your threshold of {threshold:.1f} {unit}."
            )
            triggered.append({
                "type": "current",
                "city": city,
                "metric": metric_label,
                "value": current_val,
                "threshold": threshold,
                "severity": "High" if current_val >= threshold * 1.5 else "Moderate",
                "message": msg
            })
            if alert_id and alert_id > 0:
                log_alert_trigger(city, metric, current_val, threshold, msg, alert_id=alert_id)

        # 2. Check Upcoming Forecast Peaks
        if forecast_df is not None and not forecast_df.empty:
            forecast_col = "predicted_pm2_5" if metric == "pm2_5" else "predicted_aqi"
            if forecast_col in forecast_df.columns:
                peaks = forecast_df[forecast_df[forecast_col] >= threshold]
                if not peaks.empty:
                    worst_hour = peaks.sort_values(forecast_col, ascending=False).iloc[0]
                    target_time = worst_hour.get("target_time", "upcoming hours")
                    peak_val = float(worst_hour[forecast_col])
                    h_ahead = int(worst_hour.get("horizon_hours", 0))

                    msg_fc = (
                        f"FORECAST ALERT: {city} {metric_label} is projected to reach {peak_val:.1f} {unit} "
                        f"in {h_ahead} hours ({target_time}), exceeding your threshold of {threshold:.1f} {unit}."
                    )
                    triggered.append({
                        "type": "forecast",
                        "city": city,
                        "metric": metric_label,
                        "value": peak_val,
                        "threshold": threshold,
                        "severity": "High" if peak_val >= threshold * 1.5 else "Moderate",
                        "target_time": target_time,
                        "horizon_hours": h_ahead,
                        "message": msg_fc
                    })
                    if alert_id and alert_id > 0:
                        log_alert_trigger(city, f"{metric}_forecast", peak_val, threshold, msg_fc, alert_id=alert_id)

    return triggered
