"""
AirFusion Configuration Module.
Provides centralized path management, environment variable loading,
API endpoint definitions, AQI standards, and model hyperparameter constants.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# Base Directory is the airfusion root
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

# Load .env file from PROJECT_ROOT or current working directory
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)

# Directory Paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

env_db_path = os.getenv("DB_PATH", "data/airfusion.db")
if os.path.isabs(env_db_path):
    DB_PATH = Path(env_db_path)
else:
    DB_PATH = PROJECT_ROOT / env_db_path

# Ensure required directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "").strip()

# API Endpoints
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
OPENWEATHER_AIR_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

# Default Preset Cities (Multi-State & Multi-Country Coverage)
PRESET_CITIES: Dict[str, Dict[str, Any]] = {
    # Northern India / Tri-City Focus
    "Chandigarh": {"lat": 30.7363, "lon": 76.7884, "country": "India", "state": "Chandigarh"},
    "Mohali": {"lat": 30.7046, "lon": 76.7179, "country": "India", "state": "Punjab"},
    "Panchkula": {"lat": 30.6942, "lon": 76.8606, "country": "India", "state": "Haryana"},
    "Kharar": {"lat": 30.7499, "lon": 76.6411, "country": "India", "state": "Punjab"},
    "Zirakpur": {"lat": 30.6425, "lon": 76.8173, "country": "India", "state": "Punjab"},
    "Delhi": {"lat": 28.6519, "lon": 77.2315, "country": "India", "state": "Delhi"},
    "Gurugram": {"lat": 28.4595, "lon": 77.0266, "country": "India", "state": "Haryana"},
    "Noida": {"lat": 28.5355, "lon": 77.3910, "country": "India", "state": "Uttar Pradesh"},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873, "country": "India", "state": "Rajasthan"},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462, "country": "India", "state": "Uttar Pradesh"},
    "Amritsar": {"lat": 31.6340, "lon": 74.8723, "country": "India", "state": "Punjab"},
    "Shimla": {"lat": 31.1048, "lon": 77.1734, "country": "India", "state": "Himachal Pradesh"},
    # Central, Western, Southern & Eastern India
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "country": "India", "state": "Maharashtra"},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "country": "India", "state": "Maharashtra"},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714, "country": "India", "state": "Gujarat"},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "country": "India", "state": "Karnataka"},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "country": "India", "state": "Telangana"},
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "country": "India", "state": "Tamil Nadu"},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639, "country": "India", "state": "West Bengal"},
    "Kochi": {"lat": 9.9312, "lon": 76.2673, "country": "India", "state": "Kerala"},
    # Global International Hubs
    "London": {"lat": 51.5074, "lon": -0.1278, "country": "United Kingdom", "state": "England"},
    "New York": {"lat": 40.7128, "lon": -74.0060, "country": "United States", "state": "New York"},
    "San Francisco": {"lat": 37.7749, "lon": -122.4194, "country": "United States", "state": "California"},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan", "state": "Tokyo"},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "country": "France", "state": "Ile-de-France"},
    "Dubai": {"lat": 25.2048, "lon": 55.2708, "country": "United Arab Emirates", "state": "Dubai"},
    "Singapore": {"lat": 1.3521, "lon": 103.8198, "country": "Singapore", "state": "Singapore"},
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia", "state": "New South Wales"},
    "Toronto": {"lat": 43.6532, "lon": -79.3832, "country": "Canada", "state": "Ontario"}
}

DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Chandigarh")

# Cache settings
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "900"))  # 15 minutes

# US EPA AQI Categories, Breakpoints & Health Advisories
# Standard US EPA breakpoints for PM2.5 (ug/m3) -> AQI index
AQI_CATEGORIES = [
    {
        "category": "Good",
        "aqi_min": 0,
        "aqi_max": 50,
        "pm25_min": 0.0,
        "pm25_max": 12.0,
        "color": "#00E400",  # Bright Green
        "description": "Air quality is satisfactory, and air pollution poses little or no risk.",
        "advice": {
            "general": "Ideal conditions for outdoor recreation and activities.",
            "exercise": "Safe to exercise outdoors without restrictions.",
            "mask": "No mask required.",
            "ventilation": "Open windows to bring in fresh outdoor air.",
            "sensitive": "No special precautions needed."
        }
    },
    {
        "category": "Moderate",
        "aqi_min": 51,
        "aqi_max": 100,
        "pm25_min": 12.1,
        "pm25_max": 35.4,
        "color": "#FFFF00",  # Yellow
        "description": "Air quality is acceptable. However, there may be some health concern for very sensitive people.",
        "advice": {
            "general": "Acceptable air quality for most individuals.",
            "exercise": "Safe for healthy individuals; sensitive individuals should monitor symptoms.",
            "mask": "Not needed for general public; sensitive groups may consider one during heavy exertion.",
            "ventilation": "Ventilation is acceptable during low-traffic hours.",
            "sensitive": "People with respiratory or cardiac conditions should limit prolonged outdoor exertion."
        }
    },
    {
        "category": "Unhealthy for Sensitive Groups",
        "aqi_min": 101,
        "aqi_max": 150,
        "pm25_min": 35.5,
        "pm25_max": 55.4,
        "color": "#FF7E00",  # Orange
        "description": "Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
        "advice": {
            "general": "Sensitive groups (children, elderly, asthma/heart patients) should reduce heavy outdoor work.",
            "exercise": "Take more breaks and do less intense outdoor activities.",
            "mask": "Sensitive groups should wear an N95 or KN95 mask outdoors.",
            "ventilation": "Keep windows closed during peak traffic and morning/evening smog hours.",
            "sensitive": "Keep quick-relief inhalers handy if diagnosed with asthma or COPD."
        }
    },
    {
        "category": "Unhealthy",
        "aqi_min": 151,
        "aqi_max": 200,
        "pm25_min": 55.5,
        "pm25_max": 150.4,
        "color": "#FF0000",  # Red
        "description": "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.",
        "advice": {
            "general": "Everyone may begin to experience respiratory discomfort. Limit outdoor exposure.",
            "exercise": "Avoid strenuous outdoor exercise; switch to indoor workouts.",
            "mask": "Wear a well-fitted N95 mask whenever going outside.",
            "ventilation": "Keep windows closed. Run HEPA air purifiers indoors if available.",
            "sensitive": "Avoid all outdoor physical activities; stay in clean air environments."
        }
    },
    {
        "category": "Very Unhealthy",
        "aqi_min": 201,
        "aqi_max": 300,
        "pm25_min": 150.5,
        "pm25_max": 250.4,
        "color": "#8F3F97",  # Purple
        "description": "Health alert: The risk of health effects is increased for everyone.",
        "advice": {
            "general": "Significant health risk for everyone. Stay indoors as much as possible.",
            "exercise": "Do not exercise outdoors under any circumstances.",
            "mask": "N95/FFP2 mask is mandatory outdoors.",
            "ventilation": "Seal windows and doors. Maximize indoor air filtration.",
            "sensitive": "Remain indoors in rooms equipped with air purifiers."
        }
    },
    {
        "category": "Hazardous",
        "aqi_min": 301,
        "aqi_max": 500,
        "pm25_min": 250.5,
        "pm25_max": 500.4,
        "color": "#7E0023",  # Maroon
        "description": "Health warning of emergency conditions: The entire population is more likely to be affected.",
        "advice": {
            "general": "Emergency air conditions. Extreme health warnings. Everyone must avoid all outdoor physical activity.",
            "exercise": "Prohibit all outdoor activity.",
            "mask": "High-filtration respirator (N95/N99) required for any emergency outdoor movement.",
            "ventilation": "Do not open windows. Recirculate filtered indoor air only.",
            "sensitive": "Seek medical attention if experiencing breathing distress or chest tightness."
        }
    }
]

# High pollution threshold definition (e.g. Unhealthy threshold for PM2.5 = 55.5 ug/m3 or AQI = 150)
HIGH_POLLUTION_PM25_THRESHOLD = 55.5
HIGH_POLLUTION_AQI_THRESHOLD = 150

# Target & Feature Engineering Parameters
TARGET_VARIABLE = "pm2_5"
FORECAST_HORIZONS = [24, 72]  # Hours ahead
LAG_HOURS: List[int] = [1, 3, 6, 12, 24, 48]
ROLLING_WINDOWS: List[int] = [6, 12, 24]

# Model artifact filenames
BEST_MODEL_PATH = MODELS_DIR / "best_model.joblib"
MODEL_METRICS_PATH = MODELS_DIR / "model_metrics.json"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.json"
SCALER_PATH = MODELS_DIR / "scaler.joblib"
LSTM_MODEL_PATH = MODELS_DIR / "lstm_model.pt"
