"""
Data Collection Module for AirGuard.
Fetches real-time and historical air quality and meteorological data
from Open-Meteo APIs (free, zero-config) with optional OpenWeather API fallback,
performs geocoding, and persists records into the local SQLite database.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
import requests
import pandas as pd

from src.config import (
    OPEN_METEO_GEOCODING_URL,
    OPEN_METEO_AIR_QUALITY_URL,
    OPEN_METEO_WEATHER_URL,
    OPENWEATHER_AIR_POLLUTION_URL,
    OPENWEATHER_API_KEY,
    PRESET_CITIES,
    AQI_CATEGORIES
)
from src.database import get_or_create_location, upsert_air_quality_dataframe

logger = logging.getLogger("airguard.data_collection")


def calculate_pm25_aqi(pm25: float) -> Tuple[int, str, str]:
    """
    Calculate US EPA Air Quality Index (AQI) from PM2.5 concentration (ug/m3)
    using official breakpoint formula:
    I = [(I_hi - I_lo) / (C_hi - C_lo)] * (C - C_lo) + I_lo
    """
    if pm25 is None or pd.isna(pm25) or pm25 < 0:
        return 0, "Unknown", "#808080"

    # Truncate to 1 decimal place per EPA guidelines
    c = round(float(pm25), 1)

    breakpoints = [
        (0.0, 12.0, 0, 50, "Good", "#00E400"),
        (12.1, 35.4, 51, 100, "Moderate", "#FFFF00"),
        (35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups", "#FF7E00"),
        (55.5, 150.4, 151, 200, "Unhealthy", "#FF0000"),
        (150.5, 250.4, 201, 300, "Very Unhealthy", "#8F3F97"),
        (250.5, 350.4, 301, 400, "Hazardous", "#7E0023"),
        (350.5, 500.4, 401, 500, "Hazardous", "#7E0023"),
    ]

    for c_lo, c_hi, i_lo, i_hi, category, color in breakpoints:
        if c_lo <= c <= c_hi:
            aqi = round(((i_hi - i_lo) / (c_hi - c_lo)) * (c - c_lo) + i_lo)
            return int(aqi), category, color

    if c > 500.4:
        return 500, "Hazardous", "#7E0023"

    return 0, "Good", "#00E400"


def geocode_city(city_name: str) -> Optional[Dict[str, Any]]:
    """
    Resolve city name to geographical coordinates (latitude, longitude).
    Checks preset database first, then queries Open-Meteo Geocoding API.
    """
    clean_name = city_name.strip()
    if not clean_name:
        return None

    # Check preset cities
    for preset, details in PRESET_CITIES.items():
        if preset.lower() == clean_name.lower():
            return {
                "city": preset,
                "latitude": details["lat"],
                "longitude": details["lon"],
                "country": details.get("country", ""),
                "state": details.get("state", "")
            }

    # Query Open-Meteo Geocoding API
    try:
        params = {
            "name": clean_name,
            "count": 5,
            "language": "en",
            "format": "json"
        }
        resp = requests.get(OPEN_METEO_GEOCODING_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results")
        if not results:
            logger.warning(f"No geocoding results found for '{clean_name}'")
            return None

        # Pick best match (first result)
        best = results[0]
        return {
            "city": best.get("name", clean_name),
            "latitude": round(float(best["latitude"]), 4),
            "longitude": round(float(best["longitude"]), 4),
            "country": best.get("country", ""),
            "state": best.get("admin1", "")
        }

    except requests.RequestException as e:
        logger.error(f"Geocoding network error for '{clean_name}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected geocoding error for '{clean_name}': {e}")
        return None


def fetch_current_air_quality(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Fetch current air quality & weather conditions for given coordinates.
    Returns a unified dictionary with pollutants, weather, and AQI assessment.
    """
    aq_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "us_aqi", "pm2_5", "pm10", "carbon_monoxide",
            "nitrogen_dioxide", "sulphur_dioxide", "ozone"
        ]
    }
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m", "relative_humidity_2m",
            "surface_pressure", "wind_speed_10m", "wind_direction_10m"
        ]
    }

    result: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "open-meteo"
    }

    # 1. Fetch Air Quality
    try:
        r_aq = requests.get(OPEN_METEO_AIR_QUALITY_URL, params=aq_params, timeout=10)
        r_aq.raise_for_status()
        aq_data = r_aq.json().get("current", {})

        pm25 = aq_data.get("pm2_5", 0.0)
        calculated_aqi, category, color = calculate_pm25_aqi(pm25)
        api_aqi = aq_data.get("us_aqi")
        effective_aqi = api_aqi if (api_aqi is not None and api_aqi > 0) else calculated_aqi

        result.update({
            "timestamp": aq_data.get("time", result["timestamp"]),
            "pm2_5": pm25,
            "pm10": aq_data.get("pm10", 0.0),
            "co": aq_data.get("carbon_monoxide", 0.0),
            "no2": aq_data.get("nitrogen_dioxide", 0.0),
            "so2": aq_data.get("sulphur_dioxide", 0.0),
            "o3": aq_data.get("ozone", 0.0),
            "aqi": effective_aqi,
            "aqi_category": category,
            "aqi_color": color
        })
    except Exception as e:
        logger.error(f"Error fetching current air quality: {e}")

    # 2. Fetch Weather
    try:
        r_wx = requests.get(OPEN_METEO_WEATHER_URL, params=weather_params, timeout=10)
        r_wx.raise_for_status()
        wx_data = r_wx.json().get("current", {})

        result.update({
            "temperature": wx_data.get("temperature_2m"),
            "humidity": wx_data.get("relative_humidity_2m"),
            "pressure": wx_data.get("surface_pressure"),
            "wind_speed": wx_data.get("wind_speed_10m"),
            "wind_direction": wx_data.get("wind_direction_10m")
        })
    except Exception as e:
        logger.error(f"Error fetching current weather: {e}")

    return result


def fetch_hourly_air_and_weather(
    latitude: float,
    longitude: float,
    past_days: int = 30,
    forecast_days: int = 4
) -> pd.DataFrame:
    """
    Fetch comprehensive hourly time-series combining air pollution and weather.
    Retrieves both historical past days and future forecast hours in unified DataFrame.
    """
    # 1. Fetch Air Quality Hourly
    aq_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "pm2_5", "pm10", "carbon_monoxide", "nitrogen_dioxide",
            "sulphur_dioxide", "ozone", "us_aqi"
        ],
        "past_days": past_days,
        "forecast_days": forecast_days
    }

    try:
        r_aq = requests.get(OPEN_METEO_AIR_QUALITY_URL, params=aq_params, timeout=15)
        r_aq.raise_for_status()
        aq_json = r_aq.json().get("hourly", {})
        df_aq = pd.DataFrame(aq_json)
        if not df_aq.empty and "carbon_monoxide" in df_aq.columns:
            df_aq.rename(columns={
                "carbon_monoxide": "co",
                "nitrogen_dioxide": "no2",
                "sulphur_dioxide": "so2",
                "ozone": "o3",
                "us_aqi": "aqi"
            }, inplace=True)
    except Exception as e:
        logger.error(f"Error fetching hourly air quality: {e}")
        df_aq = pd.DataFrame()

    # 2. Fetch Meteorological Hourly
    wx_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m", "relative_humidity_2m",
            "surface_pressure", "wind_speed_10m", "wind_direction_10m"
        ],
        "past_days": past_days,
        "forecast_days": forecast_days
    }

    try:
        r_wx = requests.get(OPEN_METEO_WEATHER_URL, params=wx_params, timeout=15)
        r_wx.raise_for_status()
        wx_json = r_wx.json().get("hourly", {})
        df_wx = pd.DataFrame(wx_json)
        if not df_wx.empty:
            df_wx.rename(columns={
                "temperature_2m": "temperature",
                "relative_humidity_2m": "humidity",
                "surface_pressure": "pressure",
                "wind_speed_10m": "wind_speed",
                "wind_direction_10m": "wind_direction"
            }, inplace=True)
    except Exception as e:
        logger.error(f"Error fetching hourly weather: {e}")
        df_wx = pd.DataFrame()

    # Merge on timestamp
    if df_aq.empty and df_wx.empty:
        return pd.DataFrame()
    if df_aq.empty:
        df_merged = df_wx
    elif df_wx.empty:
        df_merged = df_aq
    else:
        df_merged = pd.merge(df_aq, df_wx, on="time", how="outer")

    df_merged.rename(columns={"time": "timestamp"}, inplace=True)
    df_merged["timestamp"] = pd.to_datetime(df_merged["timestamp"])
    df_merged.sort_values("timestamp", inplace=True)
    df_merged.reset_index(drop=True, inplace=True)

    # Compute AQI category
    if "pm2_5" in df_merged.columns:
        categories = []
        for pm in df_merged["pm2_5"]:
            _, cat, _ = calculate_pm25_aqi(pm)
            categories.append(cat)
        df_merged["aqi_category"] = categories

    return df_merged


def fetch_and_store_city_data(
    city_name: str,
    past_days: int = 30,
    forecast_days: int = 4
) -> Tuple[Optional[Dict[str, Any]], pd.DataFrame]:
    """
    High-level orchestration function:
    1. Geocodes city
    2. Inserts or retrieves location record in database
    3. Fetches live/historical hourly measurements
    4. Upserts records into SQLite
    5. Returns (location_meta, combined_dataframe)
    """
    loc_meta = geocode_city(city_name)
    if not loc_meta:
        logger.warning(f"Could not geocode city '{city_name}'")
        return None, pd.DataFrame()

    loc_id = get_or_create_location(
        city=loc_meta["city"],
        latitude=loc_meta["latitude"],
        longitude=loc_meta["longitude"],
        country=loc_meta.get("country", ""),
        state=loc_meta.get("state", "")
    )
    loc_meta["location_id"] = loc_id

    # Fetch hourly data
    df = fetch_hourly_air_and_weather(
        latitude=loc_meta["latitude"],
        longitude=loc_meta["longitude"],
        past_days=past_days,
        forecast_days=forecast_days
    )

    if not df.empty:
        upsert_air_quality_dataframe(df, location_id=loc_id)
        logger.info(f"Stored {len(df)} records in SQLite for {loc_meta['city']} (ID: {loc_id})")

    return loc_meta, df


def fetch_openweather_air_pollution(
    latitude: float,
    longitude: float
) -> Optional[Dict[str, Any]]:
    """
    Secondary API source: OpenWeather Air Pollution API.
    Activated when OPENWEATHER_API_KEY is configured in .env.
    """
    if not OPENWEATHER_API_KEY:
        return None

    try:
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": OPENWEATHER_API_KEY
        }
        resp = requests.get(OPENWEATHER_AIR_POLLUTION_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("list", [])
        if not items:
            return None

        current = items[0]
        components = current.get("components", {})
        return {
            "timestamp": datetime.fromtimestamp(current.get("dt", time.time()), timezone.utc).isoformat(),
            "aqi": current.get("main", {}).get("aqi"),  # 1 to 5 scale
            "pm2_5": components.get("pm2_5"),
            "pm10": components.get("pm10"),
            "no2": components.get("no2"),
            "so2": components.get("so2"),
            "co": components.get("co"),
            "o3": components.get("o3"),
            "source": "openweather"
        }
    except Exception as e:
        logger.warning(f"OpenWeather API call failed: {e}")
        return None
