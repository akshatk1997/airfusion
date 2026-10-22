"""
About & System Documentation Page for AirGuard.
Details the end-to-end architecture, API integrations, scientific standards,
and engineering methodology of the AirGuard platform.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PRESET_CITIES
from src.predict import is_model_trained
from app.components.navbar import render_global_navbar
from app.components.design_system import (
    render_section_header,
    render_metric_tile,
    render_callout,
    render_badge,
    safe_markdown,
    ICONS
)

st.set_page_config(
    page_title="About & Architecture — AirGuard",
    page_icon="ℹ️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Global Navbar with active city synchronization
selected_city = render_global_navbar("About")

# Page Header
render_section_header(
    title="Architectural Blueprint & Platform Specifications",
    subtitle="Detailed technical overview of the real-time ingestion pipeline, machine learning core, EPA standards, and engineering architecture.",
    badge="SYSTEM SPECIFICATIONS"
)

# Top Action Toolbar
tb_col1, tb_col2 = st.columns([2.2, 1.8])
with tb_col2:
    btn1, btn2, btn3 = st.columns(3)
    with btn1:
        if st.button("⚡ Live Sensors", use_container_width=True, help="Inspect live ground sensors"):
            st.switch_page("pages/1_Live_Air_Quality.py")
    with btn2:
        if st.button("📈 Forecasting", use_container_width=True, help="View predictive trajectories"):
            st.switch_page("pages/2_Forecast.py")
    with btn3:
        if st.button("🔍 Model Insights", use_container_width=True, help="Inspect feature attributions"):
            st.switch_page("pages/6_Model_Insights.py")

# Top Platform Health & Telemetry Strip
kcol1, kcol2, kcol3, kcol4 = st.columns(4)

with kcol1:
    render_metric_tile(
        label="Monitored Centers",
        value=len(PRESET_CITIES),
        unit="cities",
        subtext="Tri-City & National Capital Region",
        icon="gauge"
    )

with kcol2:
    render_metric_tile(
        label="Ingestion Cadence",
        value=1,
        unit="hour",
        subtext="Discrete reanalysis & live sensors",
        icon="pulse"
    )

with kcol3:
    render_metric_tile(
        label="Persistence Engine",
        value="SQLite WAL",
        unit="",
        subtext="Concurrency-safe time-series tables",
        icon="chart"
    )

with kcol4:
    model_status = "Online (XGBoost)" if is_model_trained() else "Needs Retraining"
    render_metric_tile(
        label="ML Inference Core",
        value=model_status,
        unit="",
        delta="Champion Ready" if is_model_trained() else "Offline",
        delta_positive=is_model_trained(),
        subtext="Autoregressive 72h horizon",
        icon="check" if is_model_trained() else "alert"
    )

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# Deep-Dive Information Tabs
tab_arch, tab_stack, tab_standards = st.tabs([
    "📐 End-to-End System Architecture",
    "💻 Engineering Stack & API Integrations",
    "📋 US EPA Regulatory Standards"
])

# ----------------- TAB 1: SYSTEM ARCHITECTURE -----------------
with tab_arch:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    safe_markdown(
        """
        <div class="card" style="padding: var(--space-4); margin-bottom: var(--space-4);">
            <div style="font-weight: 700; font-size: var(--text-base); color: var(--color-slate-100); margin-bottom: var(--space-2);">
                End-to-End Reactive Intelligence Pipeline
            </div>
            <div style="font-size: var(--text-sm); color: var(--color-slate-300); line-height: 1.6;">
                AirGuard operates as an autonomous, closed-loop machine learning application designed for zero-latency inference and reproducible environmental modeling:
            </div>
        </div>
        """
    )

    st.markdown(
        """
```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             1. DATA SOURCES                                 │
│   Open-Meteo Air Quality API | Open-Meteo Weather API | OpenAQ Archive      │
│   (Criteria Pollutants: PM2.5, PM10, NO2, O3, CO, SO2 + Meteorology)        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (HTTP REST / JSON / Zero-Key)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    2. INGESTION & PERSISTENCE LAYER                         │
│   SQLite Database in WAL Mode (airguard.db)                                 │
│   Physical sanity validation (0.0 to 1500 µg/m³) & linear interpolation     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    3. TIME-SERIES FEATURE ENGINEERING                       │
│   - Cyclical Solar & Weekly Encoded Features: hour_sin, dayofweek_sin       │
│   - Autoregressive Particulate Lags: 1h, 3h, 6h, 12h, 24h, 48h             │
│   - Closed-Left Rolling Statistics: 6h/24h rolling mean, std, min, max      │
│   - Atmospheric Coupling Proxies: Wind Stagnation Index, Dispersion Ratio   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        4. MACHINE LEARNING ENGINE                           │
│   - Champion: XGBoost Extreme Gradient Boosting Regressor                   │
│   - Candidates: Persistence Baseline, Ridge, Random Forest, PyTorch LSTM   │
│   - Sequential Time Split: 70% Train, 15% Validation, 15% Test              │
│   - Dynamic 90% Empirical Residual Confidence Envelopes                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       5. STREAMLIT USER INTERFACE                           │
│   - Live Air Quality Telemetry & Clinical Health Recommendations            │
│   - 24h & 72h Multi-Step Particulate Trajectories with Uncertainty Ribbon  │
│   - Historical Diurnal Cycles, Weekly Patterns & Correlation Heatmaps       │
│   - Regional Multi-City Benchmarking & Ranking (Cleanest vs Polluted)       │
│   - Automated Alert Threshold Rules & Historical Incident Audit Log         │
│   - Transparent Feature Importance (XAI) & One-Click Retraining             │
└─────────────────────────────────────────────────────────────────────────────┘
```
        """
    )

# ----------------- TAB 2: TECH STACK & INTEGRATIONS -----------------
with tab_stack:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        safe_markdown(
            f"""
            <div class="card" style="padding: var(--space-4); margin-bottom: var(--space-3);">
                <div style="display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2);">
                    <div style="width: 20px; height: 20px; color: var(--color-sky-400);">{ICONS['chart']}</div>
                    <strong style="color: var(--color-slate-100); font-size: var(--text-base);">Frontend & Web Architecture</strong>
                </div>
                <ul style="margin: 0; padding-left: 20px; color: var(--color-slate-300); font-size: var(--text-sm); line-height: 1.6;">
                    <li><strong>Streamlit 1.30+</strong>: Reactive Python multi-page platform with zero JavaScript compilation overhead.</li>
                    <li><strong>Plotly 5.24+</strong>: High-contrast GPU-accelerated interactive charts with unified Modern Environmental Tech theming.</li>
                    <li><strong>Design System Tokens</strong>: Strict WCAG 2.1 AAA contrast compliance, 8-point spatial grid, and Plus Jakarta Sans / JetBrains Mono typography.</li>
                    <li><strong>Session Controller</strong>: Persistent location synchronization across all navigation pages.</li>
                </ul>
            </div>
            """
        )

        safe_markdown(
            f"""
            <div class="card" style="padding: var(--space-4);">
                <div style="display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2);">
                    <div style="width: 20px; height: 20px; color: var(--color-good);">{ICONS['check']}</div>
                    <strong style="color: var(--color-slate-100); font-size: var(--text-base);">Telemetry APIs (Zero API Key)</strong>
                </div>
                <ul style="margin: 0; padding-left: 20px; color: var(--color-slate-300); font-size: var(--text-sm); line-height: 1.6;">
                    <li><strong>Open-Meteo Air Quality API</strong>: Global hourly surface concentrations for PM2.5, PM10, NO2, O3, CO, SO2.</li>
                    <li><strong>Open-Meteo Weather API</strong>: Boundary layer meteorology including surface wind speed, humidity, temperature, and pressure.</li>
                    <li><strong>Open-Meteo Geocoding API</strong>: Sub-second coordinate resolution for any global municipal city.</li>
                    <li><strong>OpenWeather / OpenAQ</strong>: Optional secondary sensor fallback configured via <code>.env</code>.</li>
                </ul>
            </div>
            """
        )

    with c2:
        safe_markdown(
            f"""
            <div class="card" style="padding: var(--space-4); margin-bottom: var(--space-3);">
                <div style="display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2);">
                    <div style="width: 20px; height: 20px; color: var(--color-purple);">{ICONS['gauge']}</div>
                    <strong style="color: var(--color-slate-100); font-size: var(--text-base);">Machine Learning & Data Science</strong>
                </div>
                <ul style="margin: 0; padding-left: 20px; color: var(--color-slate-300); font-size: var(--text-sm); line-height: 1.6;">
                    <li><strong>XGBoost Regressor</strong>: Champion tree booster featuring column subsampling and early stopping on validation loss.</li>
                    <li><strong>PyTorch LSTM</strong>: Deep recurrent neural network modeling long-term non-linear sequential dependencies.</li>
                    <li><strong>Scikit-Learn</strong>: Ridge Regression and Random Forest benchmark baselines, robust preprocessing scalers, and metric evaluators.</li>
                    <li><strong>SHAP & Tree Attributions</strong>: Global feature weight extraction for transparent explainable AI (XAI).</li>
                </ul>
            </div>
            """
        )

        safe_markdown(
            f"""
            <div class="card" style="padding: var(--space-4);">
                <div style="display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2);">
                    <div style="width: 20px; height: 20px; color: var(--color-moderate);">{ICONS['alert']}</div>
                    <strong style="color: var(--color-slate-100); font-size: var(--text-base);">Data Persistence & Reliability</strong>
                </div>
                <ul style="margin: 0; padding-left: 20px; color: var(--color-slate-300); font-size: var(--text-sm); line-height: 1.6;">
                    <li><strong>SQLite 3 WAL Engine</strong>: Write-Ahead Logging mode enabling concurrent read operations with zero database locking contention.</li>
                    <li><strong>Automated Data Pipeline</strong>: GitHub Actions automated workflow for scheduled continuous ingestion.</li>
                    <li><strong>Pytest Automation Suite</strong>: End-to-end regression tests verifying data cleaning, feature creation, and model serialization.</li>
                    <li><strong>Environment Configuration</strong>: Safe 12-factor application secrets management with <code>.env.example</code>.</li>
                </ul>
            </div>
            """
        )

# ----------------- TAB 3: REGULATORY STANDARDS -----------------
with tab_standards:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    safe_markdown(
        """
        <div class="card" style="padding: var(--space-4); margin-bottom: var(--space-4);">
            <div style="font-weight: 700; font-size: var(--text-base); color: var(--color-slate-100); margin-bottom: var(--space-2);">
                US EPA Air Quality Index (AQI) Breakpoint Reference (PM₂.₅)
            </div>
            <div style="font-size: var(--text-sm); color: var(--color-slate-300); line-height: 1.6;">
                AirGuard utilizes the United States Environmental Protection Agency (US EPA) standard piecewise linear breakpoint equation
                to convert fine particulate mass (PM₂.₅ in µg/m³) into an intuitive 0–500 normalized index:
            </div>
        </div>
        """
    )

    safe_markdown(
        """
        <div class="card" style="padding: 0; overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: var(--text-sm); color: var(--color-slate-200);">
                <thead>
                    <tr style="border-bottom: 1px solid var(--color-slate-700); background: var(--color-slate-800); text-align: left;">
                        <th style="padding: 12px 16px; color: var(--color-slate-300); font-weight: 700;">AQI Range</th>
                        <th style="padding: 12px 16px; color: var(--color-slate-300); font-weight: 700;">Air Quality Category</th>
                        <th style="padding: 12px 16px; color: var(--color-slate-300); font-weight: 700;">PM₂.₅ Breakpoint (µg/m³)</th>
                        <th style="padding: 12px 16px; color: var(--color-slate-300); font-weight: 700;">Clinical Health Guidance</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid var(--color-slate-800);">
                        <td style="padding: 12px 16px; font-family: var(--font-mono); color: var(--color-good); font-weight: 700;">0 – 50</td>
                        <td style="padding: 12px 16px;"><span class="badge badge-good">GOOD</span></td>
                        <td style="padding: 12px 16px; font-family: var(--font-mono);">0.0 – 12.0</td>
                        <td style="padding: 12px 16px; color: var(--color-slate-300);">Air quality is satisfactory and poses little to no health risk. Ideal for outdoor activities.</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--color-slate-800);">
                        <td style="padding: 12px 16px; font-family: var(--font-mono); color: var(--color-moderate); font-weight: 700;">51 – 100</td>
                        <td style="padding: 12px 16px;"><span class="badge badge-moderate">MODERATE</span></td>
                        <td style="padding: 12px 16px; font-family: var(--font-mono);">12.1 – 35.4</td>
                        <td style="padding: 12px 16px; color: var(--color-slate-300);">Acceptable air quality. Unusually sensitive individuals should consider limiting prolonged outdoor exertion.</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--color-slate-800);">
                        <td style="padding: 12px 16px; font-family: var(--font-mono); color: var(--color-severe); font-weight: 700;">101 – 150</td>
                        <td style="padding: 12px 16px;"><span class="badge badge-warning">SENSITIVE GROUPS</span></td>
                        <td style="padding: 12px 16px; font-family: var(--font-mono);">35.5 – 55.4</td>
                        <td style="padding: 12px 16px; color: var(--color-slate-300);">Members of sensitive groups (children, elderly, asthmatics) should reduce prolonged heavy outdoor exertion.</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--color-slate-800);">
                        <td style="padding: 12px 16px; font-family: var(--font-mono); color: var(--color-severe); font-weight: 700;">151 – 200</td>
                        <td style="padding: 12px 16px;"><span class="badge badge-alert">UNHEALTHY</span></td>
                        <td style="padding: 12px 16px; font-family: var(--font-mono);">55.5 – 150.4</td>
                        <td style="padding: 12px 16px; color: var(--color-slate-300);">Everyone may begin to experience health effects; sensitive groups experience more serious symptoms. Wear N95 masks outdoors.</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--color-slate-800);">
                        <td style="padding: 12px 16px; font-family: var(--font-mono); color: var(--color-hazardous); font-weight: 700;">201 – 300</td>
                        <td style="padding: 12px 16px;"><span class="badge badge-alert">VERY UNHEALTHY</span></td>
                        <td style="padding: 12px 16px; font-family: var(--font-mono);">150.5 – 250.4</td>
                        <td style="padding: 12px 16px; color: var(--color-slate-300);">Health alert: The risk of health effects is increased for everyone. Seal indoor windows and activate HEPA filtration.</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 16px; font-family: var(--font-mono); color: var(--color-hazardous); font-weight: 700;">301 – 500+</td>
                        <td style="padding: 12px 16px;"><span class="badge badge-alert">HAZARDOUS</span></td>
                        <td style="padding: 12px 16px; font-family: var(--font-mono);">250.5 – 500.0+</td>
                        <td style="padding: 12px 16px; color: var(--color-slate-300);">Emergency warning: The entire population is likely to be affected. Avoid all outdoor physical activity.</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
    )

# Footer & Open Source Notice
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
render_callout(
    title="Open-Source Research & Public Health Notice",
    message="AirGuard is licensed under the <strong>MIT License</strong>. Engineered for environmental data scientists, municipal public health directors, and climate-conscious citizens seeking open, explainable atmospheric intelligence.",
    variant="info",
    icon="check"
)
