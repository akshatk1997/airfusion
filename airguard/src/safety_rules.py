"""
Safety Rules & Personalized Decision Support Engine for AirFusion — My Safe Outdoor Plan.
Computes multi-factor outdoor risk scores, transparent medical-free rationale,
activity recommendations, mask guidance, indoor precautions, and safe time windows.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, time as dtime
import pandas as pd
import numpy as np

logger = logging.getLogger("airfusion.safety_rules")

# ==============================================================================
# SENSITIVITY, ACTIVITY & DURATION COEFFICIENTS
# ==============================================================================

SENSITIVITY_WEIGHTS: Dict[str, float] = {
    "none": 1.0,
    "allergy": 1.25,
    "pregnancy": 1.35,
    "other respiratory sensitivity": 1.4,
    "asthma": 1.5,
    "heart condition": 1.5,
    "copd": 1.6
}

AGE_GROUP_WEIGHTS: Dict[str, float] = {
    "adult": 1.0,
    "child": 1.25,     # Developing lungs, higher ventilation rate per kg
    "senior": 1.25     # Age-related cardiopulmonary vulnerability
}

ACTIVITY_INTENSITY_WEIGHTS: Dict[str, float] = {
    "walk": 1.0,           # Baseline light aerobic
    "commute": 1.1,        # Moderate traffic proximity
    "outdoor play": 1.25,   # Spontaneous bursts, high mouth-breathing
    "cycle": 1.35,         # Elevated inhalation rate
    "outdoor work": 1.45,   # Sustained manual exertion
    "run": 1.55            # Deep alveolar particulate deposition
}

DURATION_WEIGHTS: Dict[int, float] = {
    15: 0.85,
    30: 1.0,
    45: 1.12,
    60: 1.25,
    90: 1.40,
    120: 1.55
}


def compute_base_aqi_risk(aqi: int, pm25: float) -> float:
    """
    Computes baseline environmental risk (0-100) from EPA AQI and PM2.5 concentration.
    """
    if aqi <= 50:
        # Good (0-12 ug/m3) -> Risk 5 to 25
        return 5.0 + (aqi / 50.0) * 20.0
    elif aqi <= 100:
        # Moderate (12.1-35.4 ug/m3) -> Risk 26 to 45
        return 26.0 + ((aqi - 50.0) / 50.0) * 19.0
    elif aqi <= 150:
        # Unhealthy for Sensitive Groups (35.5-55.4 ug/m3) -> Risk 46 to 65
        return 46.0 + ((aqi - 100.0) / 50.0) * 19.0
    elif aqi <= 200:
        # Unhealthy (55.5-150.4 ug/m3) -> Risk 66 to 80
        return 66.0 + ((aqi - 150.0) / 50.0) * 14.0
    elif aqi <= 300:
        # Very Unhealthy (150.5-250.4 ug/m3) -> Risk 81 to 92
        return 81.0 + ((aqi - 200.0) / 100.0) * 11.0
    else:
        # Hazardous (300+) -> Risk 93 to 100
        return min(100.0, 93.0 + ((aqi - 300.0) / 200.0) * 7.0)


def calculate_outdoor_risk_score(
    aqi: int,
    pm25: float,
    health_sensitivity: str = "none",
    age_group: str = "adult",
    activity: str = "walk",
    duration_mins: int = 30
) -> Tuple[int, str]:
    """
    Calculates composite personalized Outdoor Risk Score (0-100) and risk category.
    Returns: (risk_score: int, risk_category: str)
    Categories: Low (0-25), Moderate (26-50), High (51-75), Very High (76-100)
    """
    base_risk = compute_base_aqi_risk(aqi, pm25)

    sens_norm = health_sensitivity.lower().strip()
    sens_mult = SENSITIVITY_WEIGHTS.get(sens_norm, 1.0)

    age_norm = age_group.lower().strip()
    age_mult = AGE_GROUP_WEIGHTS.get(age_norm, 1.0)

    act_norm = activity.lower().strip()
    act_mult = ACTIVITY_INTENSITY_WEIGHTS.get(act_norm, 1.0)

    # Approximate closest duration bucket
    dur_buckets = [15, 30, 45, 60, 90, 120]
    closest_dur = min(dur_buckets, key=lambda x: abs(x - duration_mins))
    dur_mult = DURATION_WEIGHTS.get(closest_dur, 1.0)

    # Combined personal exposure multiplier
    personal_multiplier = (sens_mult * age_mult * act_mult * dur_mult) ** 0.65

    raw_score = base_risk * personal_multiplier
    final_score = int(round(min(100.0, max(0.0, raw_score))))

    if final_score <= 25:
        category = "Low"
    elif final_score <= 50:
        category = "Moderate"
    elif final_score <= 75:
        category = "High"
    else:
        category = "Very High"

    return final_score, category


def generate_personalized_advice(
    risk_score: int,
    risk_category: str,
    aqi: int,
    pm25: float,
    health_sensitivity: str,
    age_group: str,
    activity: str,
    duration_mins: int,
    preferred_time: str = "now"
) -> Dict[str, Any]:
    """
    Generates transparent, personalized rule-based advice, clear 'why' reasoning,
    actionable activity recommendation, mask guidance, and indoor precautions.
    """
    sens_clean = health_sensitivity.lower().strip()
    age_clean = age_group.lower().strip()
    act_clean = activity.lower().strip()

    # 1. Actionable Activity Recommendation
    if risk_category == "Low":
        action = f"Safe for your planned {duration_mins}-minute {act_clean}."
        if act_clean in ["run", "cycle"]:
            action += " Ambient air quality supports full outdoor aerobic training."
        else:
            action += " Enjoy your outdoor activity."
    elif risk_category == "Moderate":
        if sens_clean != "none" or age_clean in ["child", "senior"]:
            action = f"Moderate caution for a {duration_mins}-minute {act_clean}. Consider reducing intensity or shortening duration."
        else:
            action = f"Acceptable for a {duration_mins}-minute {act_clean}. Unusually sensitive individuals should monitor for throat or eye irritation."
    elif risk_category == "High":
        if act_clean in ["run", "cycle", "outdoor play"]:
            action = f"Avoid outdoor {act_clean}; switch to an indoor workout or indoor play area."
        else:
            action = f"Shorten outdoor {act_clean} to under 20 minutes, or postpone until a cleaner time window."
    else: # Very High
        action = f"Avoid all outdoor {act_clean}. Stay indoors in a clean-air filtered environment."

    # 2. Transparent 'Why' Reason
    reasons = []
    if pm25 >= 55.5 or aqi >= 151:
        reasons.append(f"ambient PM₂.₅ ({pm25:.1f} µg/m³, AQI {aqi}) is in the unhealthy range")
    elif pm25 >= 35.5 or aqi >= 101:
        reasons.append(f"ambient air pollution ({pm25:.1f} µg/m³, AQI {aqi}) exceeds the safe threshold for sensitive groups")
    else:
        reasons.append(f"ambient air quality is currently satisfactory ({pm25:.1f} µg/m³, AQI {aqi})")

    if sens_clean != "none":
        reasons.append(f"your profile includes {sens_clean.title()} sensitivity")
    if age_clean in ["child", "senior"]:
        reasons.append(f"you are planning for a {age_clean}")
    if act_clean in ["run", "cycle", "outdoor work"] and (pm25 >= 35.5 or aqi >= 101):
        reasons.append(f"{act_clean} substantially multiplies your respiratory particulate intake")

    reason_str = f"{risk_category} risk because " + ", and ".join(reasons) + "."

    # 3. Mask Guidance
    if risk_category == "Low":
        mask_guidance = "No mask or special respiratory precaution needed."
    elif risk_category == "Moderate":
        if sens_clean != "none" or age_clean in ["child", "senior"]:
            mask_guidance = "Consider a well-fitted mask if you experience throat irritation or cough."
        else:
            mask_guidance = "No mask needed for general public during short exposure."
    elif risk_category == "High":
        mask_guidance = "Wear a well-fitted N95 or KN95 particulate respirator mask if venturing outdoors."
    else:
        mask_guidance = "Strictly wear a tightly fitted N95/FFP2 mask if brief outdoor movement is unavoidable."

    # 4. Indoor Protection Guidance
    if risk_category in ["Low", "Moderate"]:
        indoor_guidance = [
            "Natural home ventilation is fine during low-traffic hours.",
            "Normal indoor activities and exercise are safe."
        ]
    elif risk_category == "High":
        indoor_guidance = [
            "Keep residential windows and vehicle vents closed.",
            "Run a HEPA air purifier in the main living/sleeping room if available.",
            "Use internal recirculation mode in vehicle AC during commute.",
            "Avoid indoor combustion sources (incense, frying, candles, smoking)."
        ]
    else:
        indoor_guidance = [
            "Seal window and door drafts; keep living spaces tightly closed.",
            "Operate HEPA air purifiers continuously on medium/high speed.",
            "Move all physical training, sports, and play entirely indoors.",
            "Create a clean-air room at home with closed doors and active filtration."
        ]

    return {
        "risk_score": risk_score,
        "risk_category": risk_category,
        "action": action,
        "reason": reason_str,
        "mask_guidance": mask_guidance,
        "indoor_guidance": indoor_guidance,
        "disclaimer": "This app provides general environmental safety decision support, not personal medical diagnosis or clinical treatment. Always follow your physician's guidance for personal health conditions."
    }


def find_safe_outdoor_windows(
    forecast_df: pd.DataFrame,
    duration_mins: int = 30,
    preferred_period: str = "now",
    user_pm25_threshold: float = 35.0,
    health_sensitivity: str = "none",
    age_group: str = "adult",
    activity: str = "walk"
) -> Dict[str, Any]:
    """
    Analyzes 24-hour hourly forecast trajectory to:
    1. Identify the safest continuous time window matching duration_mins.
    2. Identify unsafe periods exceeding threshold.
    3. Suggest an alternative cleaner window if the preferred time is contaminated.
    """
    if forecast_df.empty:
        return {
            "best_window": "Forecast data unavailable",
            "best_window_pm25": 0.0,
            "best_window_aqi": 0,
            "is_preferred_safe": True,
            "avoid_periods": [],
            "alternative_window": None,
            "hourly_timeline": []
        }

    df = forecast_df.copy()
    if "target_time" not in df.columns:
        return {"error": "Invalid forecast trajectory dataframe"}

    df["dt"] = pd.to_datetime(df["target_time"])
    df.sort_values("dt", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Duration steps in 1-hour increments (minimum 1 hour step)
    step_hours = max(1, int(round(duration_mins / 60.0)))

    # Compute rolling window average PM2.5 and risk score
    window_scores = []
    num_rows = len(df)
    for i in range(num_rows - step_hours + 1):
        chunk = df.iloc[i : i + step_hours]
        mean_pm25 = float(chunk["predicted_pm2_5"].mean())
        mean_aqi = int(round(float(chunk["predicted_aqi"].mean())))
        start_t = chunk.iloc[0]["dt"]
        end_t = start_t + pd.Timedelta(minutes=duration_mins)

        r_score, r_cat = calculate_outdoor_risk_score(
            aqi=mean_aqi,
            pm25=mean_pm25,
            health_sensitivity=health_sensitivity,
            age_group=age_group,
            activity=activity,
            duration_mins=duration_mins
        )

        window_scores.append({
            "start_time": start_t,
            "end_time": end_t,
            "label": f"{start_t.strftime('%I:%M %p')} – {end_t.strftime('%I:%M %p')}",
            "mean_pm25": mean_pm25,
            "mean_aqi": mean_aqi,
            "risk_score": r_score,
            "risk_category": r_cat,
            "hour_of_day": start_t.hour,
            "index": i
        })

    if not window_scores:
        first_t = df.iloc[0]["dt"]
        end_first_t = first_t + pd.Timedelta(minutes=duration_mins)
        window_scores = [{
            "start_time": first_t,
            "end_time": end_first_t,
            "label": f"{first_t.strftime('%I:%M %p')} – {end_first_t.strftime('%I:%M %p')}",
            "mean_pm25": float(df.iloc[0]["predicted_pm2_5"]),
            "mean_aqi": int(df.iloc[0]["predicted_aqi"]),
            "risk_score": 50,
            "risk_category": "Moderate",
            "hour_of_day": first_t.hour,
            "index": 0
        }]

    # Filter by preferred time period
    pref = preferred_period.lower().strip()
    def matches_preference(w: Dict[str, Any]) -> bool:
        h = w["hour_of_day"]
        idx = w.get("index", 0)
        if pref == "now":
            return idx == 0  # Immediate upcoming window from real-time now
        elif pref == "morning":
            return 5 <= h < 12
        elif pref == "afternoon":
            return 12 <= h < 17
        elif pref == "evening":
            return 17 <= h < 22
        elif pref == "tomorrow":
            # Windows starting after 12h or tomorrow
            return idx >= 12
        return True

    preferred_candidates = [w for w in window_scores if matches_preference(w)]
    if not preferred_candidates:
        preferred_candidates = window_scores

    # Best window in preferred period (lowest risk score)
    best_preferred = min(preferred_candidates, key=lambda x: (x["risk_score"], x["mean_pm25"]))

    # Overall absolute best window in the entire 24h forecast
    overall_best = min(window_scores, key=lambda x: (x["risk_score"], x["mean_pm25"]))

    # Find avoid periods (where predicted PM2.5 > user threshold or > 55.4 ug/m3)
    effective_thresh = max(25.0, user_pm25_threshold)
    unsafe_hours = []
    for _, row in df.iterrows():
        if row["predicted_pm2_5"] >= effective_thresh or row["predicted_aqi"] >= 151:
            unsafe_hours.append(row["dt"])

    avoid_summary = []
    if unsafe_hours:
        # Group contiguous blocks of unsafe hours
        blocks = []
        cur_block = [unsafe_hours[0]]
        for t in unsafe_hours[1:]:
            if (t - cur_block[-1]).total_seconds() <= 3600:
                cur_block.append(t)
            else:
                blocks.append(cur_block)
                cur_block = [t]
        if cur_block:
            blocks.append(cur_block)

        for b in blocks[:2]:
            if len(b) >= 20:
                avoid_summary.append(f"Avoid entire 24h horizon (PM₂.₅ forecast consistently exceeds {effective_thresh:.0f} µg/m³)")
            else:
                b_start = b[0].strftime("%I:%M %p")
                end_dt = b[-1] + pd.Timedelta(hours=1)
                b_end = end_dt.strftime("%I:%M %p")
                if b[0].date() != end_dt.date():
                    b_end += " (+1d)"
                avoid_summary.append(f"Avoid {b_start} – {b_end} (PM₂.₅ forecast exceeds {effective_thresh:.0f} µg/m³)")
    else:
        avoid_summary.append("None expected today — air is forecast to remain within your safe threshold.")

    # Alternative recommendation if preferred window has High/Very High risk
    alternative_window = None
    is_pref_safe = best_preferred["risk_score"] <= 50
    if not is_pref_safe and overall_best["label"] != best_preferred["label"]:
        alternative_window = {
            "label": overall_best["label"],
            "pm25": overall_best["mean_pm25"],
            "aqi": overall_best["mean_aqi"],
            "risk_category": overall_best["risk_category"],
            "note": f"Alternative recommendation: {overall_best['label']} offers significantly cleaner air ({overall_best['mean_pm25']:.1f} µg/m³, {overall_best['risk_category']} risk)."
        }

    # Timeline classification for visualization
    timeline = []
    for i, (_, row) in enumerate(df.head(24).iterrows()):
        p_score, p_cat = calculate_outdoor_risk_score(
            aqi=int(row["predicted_aqi"]),
            pm25=float(row["predicted_pm2_5"]),
            health_sensitivity=health_sensitivity,
            age_group=age_group,
            activity=activity,
            duration_mins=duration_mins
        )
        time_display = "Now" if i == 0 else row["dt"].strftime("%I %p")
        timeline.append({
            "time": time_display,
            "pm25": float(row["predicted_pm2_5"]),
            "aqi": int(row["predicted_aqi"]),
            "risk_score": p_score,
            "status": "Safe" if p_score <= 25 else ("Caution" if p_score <= 50 else "Avoid"),
            "color": "#10B981" if p_score <= 25 else ("#F59E0B" if p_score <= 50 else "#EF4444")
        })

    return {
        "best_window": best_preferred["label"],
        "best_window_pm25": best_preferred["mean_pm25"],
        "best_window_aqi": best_preferred["mean_aqi"],
        "best_window_category": best_preferred["risk_category"],
        "is_preferred_safe": is_pref_safe,
        "avoid_periods": avoid_summary,
        "alternative_window": alternative_window,
        "hourly_timeline": timeline
    }
