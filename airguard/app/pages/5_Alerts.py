"""
Alerts & Health Advisory Notification Workspace for AirGuard.
Evaluates custom and standard ambient safety thresholds against real-time
and +24h forecasted readings, triggers automated warnings, and maintains an incident audit log.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PRESET_CITIES, HIGH_POLLUTION_PM25_THRESHOLD
from src.database import (
    save_alert,
    fetch_alerts,
    delete_alert,
    fetch_alert_logs
)
from src.data_collection import fetch_current_air_quality, geocode_city
from src.predict import generate_forecast, is_model_trained
from src.alerts import evaluate_alerts_for_city
from app.components.navbar import render_global_navbar
from app.components.health_advisory import render_health_advisory_panel
from app.components.design_system import (
    render_section_header,
    render_metric_tile,
    render_callout,
    render_badge,
    safe_markdown,
    ICONS
)

st.set_page_config(
    page_title="Alerts & Advisories — AirGuard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="auto"
)

# Global Navbar with active city synchronization
monitor_city = render_global_navbar("Alerts")

# Page Header
render_section_header(
    title="Risk Mitigation & Automated Alert Thresholds",
    subtitle=f"Continuous threat evaluation, advance peak warnings, and medical health protocols for {monitor_city}.",
    badge="ATMOSPHERIC DEFENSE SYSTEM"
)

# Top Action Toolbar
tb_col1, tb_col2 = st.columns([2.5, 1.5])
with tb_col2:
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("🔄 Check Threats", use_container_width=True, help="Re-evaluate live thresholds"):
            st.cache_data.clear()
            st.rerun()
    with btn2:
        if st.button("⚡ Live Readings", use_container_width=True, help="Inspect live ground sensors"):
            st.switch_page("pages/1_Live_Air_Quality.py")

# Navigation Tabs
tab_monitor, tab_config, tab_history = st.tabs([
    "⚡ Active Threat Monitor",
    "⚙️ Rule Configuration",
    "📜 Incident Audit Trail"
])

# ----------------- TAB 1: ACTIVE THREAT MONITOR -----------------
with tab_monitor:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    loc = geocode_city(monitor_city)

    if not loc:
        render_callout(
            title="Location Resolution Error",
            message=f"Could not resolve geographic coordinates for '{monitor_city}'.",
            variant="alert",
            icon="alert"
        )
        st.stop()

    curr = fetch_current_air_quality(loc["latitude"], loc["longitude"])
    curr_pm = float(curr.get("pm2_5", 0.0))
    curr_aqi = int(curr.get("aqi", 0))
    category = curr.get("aqi_category", "Moderate")

    # Evaluate 24-hour predictive forecast horizon
    fc_df = None
    if is_model_trained():
        try:
            fc_df, _ = generate_forecast(monitor_city, horizon_hours=24)
        except Exception:
            pass

    # Run alert breach evaluation
    triggered = evaluate_alerts_for_city(
        city=monitor_city,
        current_pm25=curr_pm,
        current_aqi=curr_aqi,
        forecast_df=fc_df
    )

    # Top Threat Status Strip
    has_threats = len(triggered) > 0
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        render_metric_tile(
            label="Current PM₂.₅ Level",
            value=curr_pm,
            unit="µg/m³",
            subtext=f"US AQI: {curr_aqi} ({curr.get('aqi_category', 'Moderate')})",
            icon="pulse"
        )

    with stat_col2:
        max_fc_pm = float(fc_df["predicted_pm2_5"].max()) if fc_df is not None and not fc_df.empty else curr_pm
        delta_fc = max_fc_pm - curr_pm
        render_metric_tile(
            label="+24h Projected Peak",
            value=round(max_fc_pm, 1),
            unit="µg/m³",
            delta=f"{delta_fc:+.1f} µg/m³",
            delta_positive=(delta_fc <= 0),
            subtext="Highest forecasted spike",
            icon="chart"
        )

    with stat_col3:
        active_rules_count = len(fetch_alerts(active_only=True))
        render_metric_tile(
            label="Enforced Alert Rules",
            value=active_rules_count,
            unit="active",
            subtext=f"Monitoring {monitor_city} & Global",
            icon="gauge"
        )

    with stat_col4:
        threat_count = len(triggered)
        render_metric_tile(
            label="Active Breaches",
            value=threat_count,
            unit="threats",
            delta="CLEAR" if threat_count == 0 else f"{threat_count} BREACHES",
            delta_positive=(threat_count == 0),
            subtext="Safety threshold triggers",
            icon="alert" if threat_count > 0 else "check"
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Active Breach Notification Banners
    if triggered:
        for t in triggered:
            is_severe = t.get("severity") == "High"
            border_color = "var(--color-severe)" if is_severe else "var(--color-moderate)"
            bg_color = "rgba(239, 68, 68, 0.08)" if is_severe else "rgba(245, 158, 11, 0.08)"
            badge_class = "badge-alert" if is_severe else "badge-warning"
            action_label = "🔴 IMMEDIATE ACTION REQUIRED" if t["type"] == "current" else "🟠 ADVANCE PEAK WARNING (+24H)"

            safe_markdown(
                f"""
                <div class="card" style="border-left: 4px solid {border_color}; background: {bg_color}; padding: var(--space-4); margin-bottom: var(--space-3);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-2);">
                        <span class="badge {badge_class}">{action_label}</span>
                        <span style="font-size: var(--text-xs); color: var(--color-slate-400); font-family: var(--font-mono);">
                            Severity Tier: <strong style="color: var(--color-slate-200);">{t.get('severity', 'Moderate').upper()}</strong>
                        </span>
                    </div>
                    <div style="color: var(--color-slate-100); font-weight: 600; font-size: var(--text-base); line-height: 1.5;">
                        {t['message']}
                    </div>
                </div>
                """
            )
    else:
        if curr_aqi > 100:
            render_callout(
                title="Custom Thresholds Compliant — Ambient Air Quality Elevated",
                message=f"No custom alert trigger breaches detected for {monitor_city}. Ambient air currently registers PM₂.₅ {curr_pm:.1f} µg/m³ (AQI {curr_aqi}, {category}). While no custom rule was tripped, ambient conditions warrant precautionary attention for sensitive cohorts.",
                variant="warning",
                icon="alert"
            )
        else:
            render_callout(
                title="Atmospheric Safety Confirmed — All Clear",
                message=f"No threshold breaches detected for {monitor_city}. Current PM₂.₅ of {curr_pm:.1f} µg/m³ (AQI {curr_aqi}) complies with all configured alert safety rules and clean baseline standards.",
                variant="success",
                icon="check"
            )

    # Health Advisory Panel
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    render_health_advisory_panel(curr_aqi)

# ----------------- TAB 2: RULE CONFIGURATION -----------------
with tab_config:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    render_section_header(
        title="Register Custom Safety Alert Rule",
        subtitle="Establish personal air quality thresholds for sensitive cohorts, children, or elderly family members.",
        badge="THRESHOLD RULE ENGINE"
    )

    with st.form("new_alert_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            alert_city = st.selectbox(
                "Monitored Target Location",
                options=["All Monitored Cities"] + list(PRESET_CITIES.keys()),
                index=1 if monitor_city in PRESET_CITIES else 0,
                help="Select a specific city or apply globally across all locations"
            )
        with col2:
            alert_metric = st.selectbox(
                "Monitored Indicator",
                options=["PM2.5 Particulate (µg/m³)", "US Air Quality Index (AQI)"],
                help="Choose whether to trigger on raw particulate mass or normalized index"
            )
        with col3:
            default_val = 55.4 if "PM2.5" in alert_metric else 150.0
            threshold_val = st.number_input(
                "Breach Trigger Threshold",
                min_value=1.0,
                max_value=500.0,
                value=default_val,
                step=5.0,
                help="Alert will fire when real-time or forecasted values equal or exceed this level"
            )

        alert_email = st.text_input(
            "Notification Dispatch Channel (Email / Webhook)",
            value="",
            placeholder="e.g. alerts@facility.org (optional for logging)"
        )

        submitted = st.form_submit_button("⚡ Register Alert Rule", use_container_width=True)
        if submitted:
            metric_key = "pm2_5" if "PM2.5" in alert_metric else "aqi"
            city_val = "all" if alert_city == "All Monitored Cities" else alert_city
            alert_id = save_alert(
                city=city_val,
                metric=metric_key,
                threshold_value=threshold_val,
                condition="greater_than",
                email=alert_email
            )
            st.success(f"Safety Rule #{alert_id} successfully registered for {alert_city} at threshold ≥ {threshold_val}!")
            st.rerun()

    # Active Rules Table & Management
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    render_section_header(
        title="Active Enforced Safety Rules",
        subtitle="Current monitors active in the SQLite persistence database.",
        badge="RULE REGISTRY"
    )

    active_rules = fetch_alerts(active_only=True)
    if active_rules:
        df_rules = pd.DataFrame(active_rules)
        display_rules = df_rules[["id", "city", "metric", "threshold_value", "email", "created_at"]].copy()
        display_rules.rename(columns={
            "id": "Rule ID",
            "city": "Scope",
            "metric": "Telemetry",
            "threshold_value": "Threshold",
            "email": "Recipient",
            "created_at": "Registered At"
        }, inplace=True)
        st.dataframe(display_rules, use_container_width=True, hide_index=True)

        # Deletion Control
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        del_col1, del_col2 = st.columns([1.5, 2.5])
        with del_col1:
            valid_ids = df_rules["id"].tolist()
            rule_id_del = st.selectbox("Select Rule to Revoke", options=valid_ids)
        with del_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Revoke Selected Rule", type="secondary"):
                delete_alert(int(rule_id_del))
                st.info(f"Rule #{rule_id_del} revoked successfully.")
                st.rerun()
    else:
        render_callout(
            title="Standard Baseline Guidelines Active",
            message="No custom user rules configured. AirGuard is operating under standard national EPA air safety thresholds (PM₂.₅ ≥ 55.4 µg/m³, AQI ≥ 150).",
            variant="info",
            icon="info"
        )

# ----------------- TAB 3: INCIDENT AUDIT TRAIL -----------------
with tab_history:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    render_section_header(
        title="Triggered Threat Incident Audit Trail",
        subtitle="Immutable archival log of all real-time and predictive threshold breaches recorded by AirGuard.",
        badge="AUDIT LOGS"
    )

    logs = fetch_alert_logs(limit=100)
    if logs:
        df_logs = pd.DataFrame(logs)
        display_logs = df_logs[["id", "city", "metric", "value", "threshold", "message", "triggered_at"]].copy()
        display_logs.rename(columns={
            "id": "Incident ID",
            "city": "Location",
            "metric": "Parameter",
            "value": "Measured Value",
            "threshold": "Breached Limit",
            "message": "Incident Summary",
            "triggered_at": "Timestamp (UTC)"
        }, inplace=True)
        st.dataframe(display_logs, use_container_width=True, hide_index=True)

        # CSV Download of Incident Logs
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        csv_logs = df_logs.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📥 Export Incident Audit Trail ({len(df_logs)} Breaches)",
            data=csv_logs,
            file_name="airguard_breach_audit_trail.csv",
            mime="text/csv"
        )
    else:
        render_callout(
            title="Clean Incident History",
            message="No threshold breach incidents have been triggered in the database audit log.",
            variant="success",
            icon="check"
        )
