"""
Unit tests for the Safety Rules & Risk Decision Engine.
Tests risk scoring, sensitivity multipliers, duration weighting, advice generation, and safe window finding.
"""

import sys
from pathlib import Path
import pandas as pd
import pytest

# Add airguard root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.safety_rules import (
    calculate_outdoor_risk_score,
    generate_personalized_advice,
    find_safe_outdoor_windows,
    compute_base_aqi_risk
)


def test_base_aqi_risk():
    # Good air quality (AQI 25) should produce low base risk
    r_good = compute_base_aqi_risk(25, 6.0)
    assert 5.0 <= r_good <= 25.0

    # Unhealthy (AQI 175) should produce high base risk
    r_unhealthy = compute_base_aqi_risk(175, 100.0)
    assert 65.0 <= r_unhealthy <= 80.0

    # Hazardous (AQI 350) should produce extreme base risk
    r_haz = compute_base_aqi_risk(350, 320.0)
    assert r_haz >= 90.0


def test_sensitivity_multiplier_increases_risk():
    # For identical air quality, someone with asthma or COPD must have higher risk score than a healthy adult
    score_healthy, cat_healthy = calculate_outdoor_risk_score(
        aqi=90,
        pm25=30.0,
        health_sensitivity="none",
        age_group="adult",
        activity="walk",
        duration_mins=30
    )

    score_asthma, cat_asthma = calculate_outdoor_risk_score(
        aqi=90,
        pm25=30.0,
        health_sensitivity="asthma",
        age_group="adult",
        activity="walk",
        duration_mins=30
    )

    assert score_asthma > score_healthy
    assert score_asthma >= score_healthy * 1.15


def test_activity_intensity_increases_risk():
    # High-aerobic exertion (running) must produce higher risk than walking
    score_walk, _ = calculate_outdoor_risk_score(
        aqi=110,
        pm25=40.0,
        health_sensitivity="none",
        activity="walk",
        duration_mins=45
    )

    score_run, _ = calculate_outdoor_risk_score(
        aqi=110,
        pm25=40.0,
        health_sensitivity="none",
        activity="run",
        duration_mins=45
    )

    assert score_run > score_walk


def test_personalized_advice_contents():
    advice = generate_personalized_advice(
        risk_score=78,
        risk_category="Very High",
        aqi=160,
        pm25=75.0,
        health_sensitivity="asthma",
        age_group="adult",
        activity="run",
        duration_mins=60
    )

    assert advice["risk_score"] == 78
    assert advice["risk_category"] == "Very High"
    assert "Avoid" in advice["action"]
    assert "asthma" in advice["reason"].lower()
    assert "N95" in advice["mask_guidance"]
    assert len(advice["indoor_guidance"]) >= 2
    assert "disclaimer" in advice


def test_find_safe_outdoor_windows():
    # Create sample 24-hour forecast where morning is clean and evening is smoggy
    hours = pd.date_range("2026-10-23 00:00:00", periods=24, freq="h")
    # Low PM2.5 in morning (hours 6-10: 15 ug/m3), High in evening (hours 17-21: 110 ug/m3)
    pm25_vals = [60.0] * 6 + [15.0] * 5 + [45.0] * 6 + [110.0] * 5 + [80.0] * 2
    aqi_vals = [120] * 6 + [45] * 5 + [100] * 6 + [180] * 5 + [150] * 2

    df_fc = pd.DataFrame({
        "target_time": [h.strftime("%Y-%m-%d %H:%M") for h in hours],
        "predicted_pm2_5": pm25_vals,
        "predicted_aqi": aqi_vals
    })

    windows = find_safe_outdoor_windows(
        forecast_df=df_fc,
        duration_mins=60,
        preferred_period="morning",
        user_pm25_threshold=35.0,
        health_sensitivity="none",
        activity="run"
    )

    assert "best_window" in windows
    assert windows["best_window_pm25"] < 30.0
    assert len(windows["avoid_periods"]) > 0
    assert len(windows["hourly_timeline"]) == 24
