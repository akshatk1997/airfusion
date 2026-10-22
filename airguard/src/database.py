"""
Database Management Module for AirGuard.
Manages SQLite connection, schema migrations, and queries for locations,
air quality measurements, forecasts, and user-configured alerts.
"""

from __future__ import annotations

import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd

from src.config import DB_PATH

logger = logging.getLogger("airguard.database")


def get_db_connection(db_path: Optional[Path | str] = None) -> sqlite3.Connection:
    """
    Establish a thread-safe connection to the SQLite database.
    """
    path = str(db_path or DB_PATH)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for concurrent reads and writes
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except Exception as e:
        logger.warning(f"Could not set PRAGMA journal_mode: {e}")
    return conn


def init_db(db_path: Optional[Path | str] = None) -> None:
    """
    Create database tables and indexes if they do not exist.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Locations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            state TEXT,
            country TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(city, latitude, longitude)
        );
    """)

    # 2. Air Quality and Weather Records Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS air_quality_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            aqi INTEGER,
            aqi_category TEXT,
            pm2_5 REAL,
            pm10 REAL,
            no2 REAL,
            o3 REAL,
            co REAL,
            so2 REAL,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            wind_direction REAL,
            pressure REAL,
            source TEXT DEFAULT 'open-meteo',
            raw_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id),
            UNIQUE(location_id, timestamp)
        );
    """)

    # 3. Forecast Records Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecast_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            forecast_time TEXT NOT NULL,
            target_time TEXT NOT NULL,
            horizon_hours INTEGER NOT NULL,
            predicted_pm2_5 REAL NOT NULL,
            predicted_aqi INTEGER,
            lower_ci REAL,
            upper_ci REAL,
            model_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        );
    """)

    # 4. User Alerts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            metric TEXT NOT NULL DEFAULT 'pm2_5',
            threshold_value REAL NOT NULL,
            condition TEXT NOT NULL DEFAULT 'greater_than',
            email TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 5. Alert Trigger Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER,
            city TEXT NOT NULL,
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metric TEXT NOT NULL,
            value REAL NOT NULL,
            threshold REAL NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (alert_id) REFERENCES alerts (id)
        );
    """)

    # Indexes for fast time-series queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_loc_time ON air_quality_records(location_id, timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_forecast_loc_time ON forecast_records(location_id, target_time);")

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully at %s", db_path or DB_PATH)


def get_or_create_location(
    city: str,
    latitude: float,
    longitude: float,
    country: str = "",
    state: str = "",
    db_path: Optional[Path | str] = None
) -> int:
    """
    Retrieve location id or create a new location entry.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    clean_city = city.strip().title()

    # Search by city name and approx coordinates (within 0.05 deg ~ 5km)
    cursor.execute("""
        SELECT id FROM locations
        WHERE LOWER(city) = LOWER(?)
        LIMIT 1;
    """, (clean_city,))
    row = cursor.fetchone()

    if row:
        loc_id = int(row["id"])
    else:
        cursor.execute("""
            INSERT INTO locations (city, state, country, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
        """, (clean_city, state, country, latitude, longitude))
        conn.commit()
        loc_id = cursor.lastrowid

    conn.close()
    return loc_id


def upsert_air_quality_dataframe(
    df: pd.DataFrame,
    location_id: int,
    source: str = "open-meteo",
    db_path: Optional[Path | str] = None
) -> int:
    """
    Upsert a pandas DataFrame of air quality and weather records into SQLite.
    Expected columns: timestamp, pm2_5, pm10, no2, o3, co, so2, aqi,
                      aqi_category, temperature, humidity, wind_speed,
                      wind_direction, pressure.
    """
    if df.empty:
        return 0

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Ensure required columns exist with None defaults if missing
    columns = [
        "timestamp", "aqi", "aqi_category", "pm2_5", "pm10",
        "no2", "o3", "co", "so2", "temperature", "humidity",
        "wind_speed", "wind_direction", "pressure"
    ]
    df_copy = df.copy()
    for col in columns:
        if col not in df_copy.columns:
            df_copy[col] = None

    rows = []
    for _, r in df_copy.iterrows():
        rows.append((
            location_id,
            str(r["timestamp"]),
            int(r["aqi"]) if pd.notnull(r["aqi"]) else None,
            str(r["aqi_category"]) if pd.notnull(r["aqi_category"]) else None,
            float(r["pm2_5"]) if pd.notnull(r["pm2_5"]) else None,
            float(r["pm10"]) if pd.notnull(r["pm10"]) else None,
            float(r["no2"]) if pd.notnull(r["no2"]) else None,
            float(r["o3"]) if pd.notnull(r["o3"]) else None,
            float(r["co"]) if pd.notnull(r["co"]) else None,
            float(r["so2"]) if pd.notnull(r["so2"]) else None,
            float(r["temperature"]) if pd.notnull(r["temperature"]) else None,
            float(r["humidity"]) if pd.notnull(r["humidity"]) else None,
            float(r["wind_speed"]) if pd.notnull(r["wind_speed"]) else None,
            float(r["wind_direction"]) if pd.notnull(r["wind_direction"]) else None,
            float(r["pressure"]) if pd.notnull(r["pressure"]) else None,
            source
        ))

    cursor.executemany("""
        INSERT OR REPLACE INTO air_quality_records (
            location_id, timestamp, aqi, aqi_category, pm2_5, pm10,
            no2, o3, co, so2, temperature, humidity,
            wind_speed, wind_direction, pressure, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, rows)

    conn.commit()
    inserted_count = cursor.rowcount
    conn.close()
    return inserted_count


def fetch_historical_records(
    city: Optional[str] = None,
    location_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: Optional[Path | str] = None
) -> pd.DataFrame:
    """
    Fetch historical records filtered by city/location and date range.
    Returns sorted pandas DataFrame with parsed timestamps.
    """
    conn = get_db_connection(db_path)
    query = """
        SELECT r.*, l.city, l.state, l.country, l.latitude, l.longitude
        FROM air_quality_records r
        JOIN locations l ON r.location_id = l.id
        WHERE 1=1
    """
    params: List[Any] = []

    if location_id is not None:
        query += " AND r.location_id = ?"
        params.append(location_id)
    elif city:
        query += " AND LOWER(l.city) = LOWER(?)"
        params.append(city.strip())

    if start_date:
        query += " AND r.timestamp >= ?"
        params.append(start_date)
    if end_date:
        query += " AND r.timestamp <= ?"
        params.append(end_date)

    query += " ORDER BY r.timestamp ASC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if not df.empty and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed")
    return df


def fetch_latest_record(
    city: str,
    db_path: Optional[Path | str] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch the most recent air quality record for a specific city.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, l.city, l.latitude, l.longitude
        FROM air_quality_records r
        JOIN locations l ON r.location_id = l.id
        WHERE LOWER(l.city) = LOWER(?)
        ORDER BY r.timestamp DESC
        LIMIT 1;
    """, (city.strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def insert_forecast_records(
    forecast_rows: List[Dict[str, Any]],
    db_path: Optional[Path | str] = None
) -> None:
    """
    Insert forecasted values for a given location.
    """
    if not forecast_rows:
        return

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    rows = []
    for f in forecast_rows:
        rows.append((
            f["location_id"],
            f.get("forecast_time", datetime.utcnow().isoformat()),
            f["target_time"],
            f["horizon_hours"],
            f["predicted_pm2_5"],
            f.get("predicted_aqi"),
            f.get("lower_ci"),
            f.get("upper_ci"),
            f.get("model_name", "xgboost")
        ))

    cursor.executemany("""
        INSERT INTO forecast_records (
            location_id, forecast_time, target_time, horizon_hours,
            predicted_pm2_5, predicted_aqi, lower_ci, upper_ci, model_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()


def save_alert(
    city: str,
    metric: str = "pm2_5",
    threshold_value: float = 55.5,
    condition: str = "greater_than",
    email: str = "",
    db_path: Optional[Path | str] = None
) -> int:
    """
    Register a new user alert rule.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (city, metric, threshold_value, condition, email, active)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (city.strip().title(), metric, threshold_value, condition, email))
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id


def fetch_alerts(
    active_only: bool = True,
    db_path: Optional[Path | str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch configured alerts.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    query = "SELECT * FROM alerts"
    if active_only:
        query += " WHERE active = 1"
    query += " ORDER BY created_at DESC"
    cursor.execute(query)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def delete_alert(alert_id: int, db_path: Optional[Path | str] = None) -> None:
    """
    Delete an alert by ID.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()


def log_alert_trigger(
    city: str,
    metric: str,
    value: float,
    threshold: float,
    message: str,
    alert_id: Optional[int] = None,
    db_path: Optional[Path | str] = None
) -> None:
    """
    Log an event when an alert threshold is breached.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alert_logs (alert_id, city, metric, value, threshold, message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (alert_id, city.strip().title(), metric, value, threshold, message))
    conn.commit()
    conn.close()


def fetch_alert_logs(limit: int = 50, db_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
    """
    Fetch recent alert logs.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM alert_logs
        ORDER BY triggered_at DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
