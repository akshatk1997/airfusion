"""
Unit tests for data collection, geocoding, and database operations.
"""

import os
import sys
from pathlib import Path
import pytest
import pandas as pd

# Add airguard root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import init_db, get_or_create_location, upsert_air_quality_dataframe, fetch_historical_records, fetch_all_locations
from src.data_collection import geocode_city, calculate_pm25_aqi, fetch_current_air_quality


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_airguard.db"
    init_db(db_file)
    return db_file


def test_calculate_pm25_aqi():
    # Test Good
    aqi, cat, color = calculate_pm25_aqi(8.0)
    assert aqi <= 50
    assert cat == "Good"
    assert color == "#00E400"

    # Test Moderate
    aqi, cat, _ = calculate_pm25_aqi(25.0)
    assert 51 <= aqi <= 100
    assert cat == "Moderate"

    # Test Unhealthy for Sensitive Groups
    aqi, cat, _ = calculate_pm25_aqi(45.0)
    assert 101 <= aqi <= 150
    assert cat == "Unhealthy for Sensitive Groups"

    # Test Unhealthy
    aqi, cat, _ = calculate_pm25_aqi(85.0)
    assert 151 <= aqi <= 200
    assert cat == "Unhealthy"

    # Test Very Unhealthy
    aqi, cat, _ = calculate_pm25_aqi(180.0)
    assert 201 <= aqi <= 300
    assert cat == "Very Unhealthy"

    # Test Hazardous
    aqi, cat, _ = calculate_pm25_aqi(320.0)
    assert aqi > 300
    assert cat == "Hazardous"


def test_geocoding_preset():
    res = geocode_city("Chandigarh")
    assert res is not None
    assert res["city"] == "Chandigarh"
    assert abs(res["latitude"] - 30.7363) < 0.01
    assert abs(res["longitude"] - 76.7884) < 0.01


def test_database_crud(temp_db):
    loc_id = get_or_create_location("Mohali", 30.7046, 76.7179, "India", "Punjab", db_path=temp_db)
    assert loc_id > 0

    # Idempotent
    loc_id_2 = get_or_create_location("Mohali", 30.7046, 76.7179, db_path=temp_db)
    assert loc_id == loc_id_2

    # Insert records
    df = pd.DataFrame([
        {
            "timestamp": "2026-10-22 08:00:00",
            "aqi": 85,
            "aqi_category": "Moderate",
            "pm2_5": 28.5,
            "pm10": 45.2,
            "no2": 15.1,
            "o3": 35.0,
            "co": 500.0,
            "so2": 8.0,
            "temperature": 24.5,
            "humidity": 55.0,
            "wind_speed": 4.2,
            "wind_direction": 280,
            "pressure": 1012.0
        }
    ])
    inserted = upsert_air_quality_dataframe(df, location_id=loc_id, db_path=temp_db)
    assert inserted >= 1

    fetched_df = fetch_historical_records(city="Mohali", db_path=temp_db)
    assert len(fetched_df) == 1
    assert fetched_df.iloc[0]["pm2_5"] == 28.5

    # Test fetch_all_locations
    all_locs = fetch_all_locations(db_path=temp_db)
    assert len(all_locs) == 1
    assert all_locs[0]["city"] == "Mohali"


def test_geocoding_custom_multi_token():
    res = geocode_city("Panchkula, Haryana, India")
    assert res is not None
    assert "Panchkula" in res["city"]
    assert res["latitude"] > 0
    assert res["longitude"] > 0
    assert "name" in res
    assert "state" in res
