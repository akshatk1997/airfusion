# AirFusion Technical Architecture & Integrity Audit (Phase 0)

**Date:** 2026-10-30  
**Branch:** `fix/audit-and-cnn`  
**Auditor:** Senior ML Engineer & Full-Stack Developer  
**Repository:** [github.com/akshatk1997/airfusion](https://github.com/akshatk1997/airfusion)  

---

## 1. Executive Findings & Ground Truth Summary

| Aspect | Claim in Documentation / UI | Actual Production Ground Truth |
| :--- | :--- | :--- |
| **Active Deployment** | Full-stack ML Pipeline (LightGBM + XGBoost + CatBoost + LSTM) | Client-side static single-page application (`public/index.html`) served via Vercel. `api/index.py` is a 30-line HTTP fallback returning `index.html`. |
| **Model Execution** | Real-time inference via trained ML models | **No Python ML models run on Vercel.** `airfusion/`, `models/`, `tests/`, and SQLite `.db` are ignored by `.vercelignore`. All live telemetry is queried client-side from Open-Meteo APIs. |
| **Model Metrics** | $R^2 = 0.941$, $\text{MAE} = 5.61\,\mu\text{g/m}^3$, $\text{RMSE} = 8.42\,\mu\text{g/m}^3$ (hardcoded in UI) | Offline trained XGBoost on 24h lead achieves test $R^2 = 0.0615$, $\text{MAE} = 20.47\,\mu\text{g/m}^3$, $\text{RMSE} = 25.61\,\mu\text{g/m}^3$ (`airfusion/models/model_metrics.json`). |
| **Dependencies** | LightGBM, CatBoost claimed in UI & README | Neither `lightgbm` nor `catboost` is present in root or `airfusion/` `requirements.txt`. |
| **Deep Learning (LSTM)** | Active LSTM model projections | PyTorch LSTM is implemented and trained offline (`lstm_model.pt`, test $R^2 = 0.0296$, $\text{MAE} = 22.13\,\mu\text{g/m}^3$), but is **not deployed or called** for inference. |
| **Training Target Data** | CAAQMS / CPCB ground station telemetry | Data ingested via Open-Meteo Air Quality API, which outputs CAMS (Copernicus Atmosphere Monitoring Service) atmospheric model reanalysis, not raw CPCB physical sensor feeds. |
| **Continuous Integration** | Static badge: `pytest-60/60 Passing` | Workflow triggers only on cron schedule, not on `push` or `pull_request`. Actual test suite has 62 tests: **54 Passed, 8 Skipped, 0 Failed**. |
| **Cigarette Equivalence** | $(\text{Inhaled micrograms}) / 22.0$ | Overstates exposure by $\approx 10\times$. True Berkeley Earth rule: $22\,\mu\text{g/m}^3$ averaged over 24 hours $\approx 1$ cigarette. |
| **Satellite AOD Attributions**| Sentinel-5P TROPOMI Level-2 AOD at 440nm & 870nm | TROPOMI measures UV Aerosol Index (UVAI at 354/388nm), not multi-wavelength visible/NIR AOD (440/870nm), which comes from ground sun-photometers (AERONET) or MODIS. |
| **API Endpoints** | Documented `/api/v1/telemetry`, `/api/v1/forecast/72h`, etc. | Non-existent in `api/index.py`. The serverless endpoint only serves static HTML. |

---

## 2. Telemetry & Forecast Data Pipeline (Audit Item 1)

### 2.1 Live Web Application (`public/index.html`)
The live production website deployed on Vercel is a standalone single-page web app. All numbers shown to the user originate from:
1. **Live Ground Telemetry & Pollutants**:
   - `fetch('https://air-quality-api.open-meteo.com/v1/air-quality?latitude=...&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi&hourly=pm2_5,us_aqi')`
   - Returns real-time ambient concentrations: $\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{NO}_2$, $\text{SO}_2$, $\text{O}_3$, $\text{CO}$, and US EPA AQI.
2. **Live Synoptic Weather**:
   - `fetch('https://api.open-meteo.com/v1/forecast?latitude=...&current=temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,wind_speed_10m,wind_direction_10m,uv_index,weather_code,precipitation&hourly=...')`
   - Returns meteorological parameters: temperature, humidity, wind velocity/direction, barometric surface pressure, WMO weather codes, and precipitation probability.
3. **Derived Physics (Client-Side JavaScript)**:
   - Magnus-Tetens Dew Point ($T_d$) and depression ($\Delta T = T - T_d$).
   - Planetary Boundary Layer Height estimate ($PBLH = 1200 \cdot (1 - RH/100) + 35 \cdot U_{10}$).
   - Ventilation Index ($VI = PBLH \times U_{10}/3.6$).
   - Gaussian Plume downwind dispersion: $C(x,y,z) = \frac{Q}{2\pi u \sigma_y \sigma_z} \exp\left(-\frac{y^2}{2\sigma_y^2}\right)\left[\exp\left(-\frac{(z-H)^2}{2\sigma_z^2}\right) + \exp\left(-\frac{(z+H)^2}{2\sigma_z^2}\right)\right]$.
   - Köhler hygroscopic growth: $f(RH) = 1 + a \cdot \left(\frac{RH}{100 - RH}\right)^b$.
   - Ångström Turbidity Exponent: $\alpha = -\frac{\ln(\tau_{440}/\tau_{870})}{\ln(440/870)}$.
4. **Heuristic & Simulated Numbers**:
   - **Safe Outdoor Schedule**: Simple Mode hourly PM2.5 progression applies fixed cyclical factors:
     `factor = (h >= 7 && h <= 10) ? 1.35 : ((h >= 12 && h <= 16) ? 0.8 : ((h >= 19 && h <= 23) ? 1.45 : 1.0))`.
   - **Model Diagnostics UI**: The metrics table displays hardcoded values ($R^2 = 0.941$, $\text{MAE} = 5.61\,\mu\text{g/m}^3$) and claims LightGBM/CatBoost architectures that do not run.

### 2.2 Local Streamlit Application (`airfusion/`)
When run locally via `streamlit run airfusion/app/Home.py`:
- Ingests data through `airfusion/src/data_collection.py` into local SQLite (`airfusion/data/airfusion.db`).
- Generates 24h and 72h forecasts using `airfusion/src/predict.py`, which loads `airfusion/models/best_model.joblib`.
- This pipeline is functional locally, but **completely omitted from Vercel deployment** due to `.vercelignore`.

---

## 3. Deep Learning & LSTM Audit (Audit Item 2)

- **Architecture:** `AirQualityLSTM` in `airfusion/src/train_model.py` (2-layer LSTM with 48/64 hidden units, 20% dropout, FC projection layers).
- **Artifact:** Serialized weights exist at `airfusion/models/lstm_model.pt` (160 KB).
- **Offline Benchmark:**
  - Validation: $\text{MAE} = 18.796\,\mu\text{g/m}^3$, $\text{RMSE} = 23.962\,\mu\text{g/m}^3$, $R^2 = 0.1339$.
  - Test: $\text{MAE} = 22.131\,\mu\text{g/m}^3$, $\text{RMSE} = 26.039\,\mu\text{g/m}^3$, $R^2 = 0.0296$.
- **Production Usage:** **None.** XGBoost outperformed LSTM during model selection, so only XGBoost is bundled into `best_model.joblib`. Furthermore, PyTorch (700+ MB) is not deployed to Vercel.

---

## 4. Training Target, Geographic Scope & Horizon (Audit Item 3)

- **Ground Truth Target vs Modelled Atmosphere:**
  The ingestion pipeline in `airfusion/src/data_collection.py` queries `https://air-quality-api.open-meteo.com/v1/air-quality`. Open-Meteo's air quality data is driven by CAMS (Copernicus Atmosphere Monitoring Service) global atmospheric models and European regional ensembles, **not physical ground station telemetry from CPCB/CAAQMS**.
- **Geographic Scope:**
  Four northern Indian airsheds: Chandigarh, Mohali, Kharar, and Delhi.
- **Sample Distribution:**
  - 3,242 training observations (70%).
  - 695 validation observations (15%).
  - 695 chronological test observations (15%).
- **Forecast Horizons:**
  - Primary target: `target_lead_24h` (+24 hours).
  - Secondary targets: `target_lead_1h` (autoregressive stepping) and `target_lead_72h` (+72 hours).

---

## 5. CI/CD Workflow & Test Suite Results (Audit Item 4)

- **Workflow Configuration (`.github/workflows/update_data.yml`):**
  - Triggers: Scheduled cron (`0 */6 * * *`) and `workflow_dispatch`.
  - **Defect:** Does not trigger on `push` or `pull_request`, meaning code changes currently merge without automated testing.
- **Execution Run (Python 3.14 / pytest 9.1.1):**
  - **Total Collected Items:** 62
  - **Passed:** 54
  - **Skipped:** 8 (Browser UI tests requiring a running local Streamlit server)
  - **Failed:** 0
  - **Conclusion:** The README badge claiming `pytest-60/60 Passing` is inaccurate. The true result is **54 passed, 8 skipped**.

---

## 6. Third-Party Services Inventory (Audit Item 5)

| Service | Protocol / URL | Purpose | User Privacy Implication |
| :--- | :--- | :--- | :--- |
| **Open-Meteo Air Quality** | `https://air-quality-api.open-meteo.com` | Fetch ambient criteria pollutant readings | Client IP and coordinates sent |
| **Open-Meteo Forecast** | `https://api.open-meteo.com` | Fetch weather, pressure, wind, and WMO codes | Client IP and coordinates sent |
| **Open-Meteo Geocoding** | `https://geocoding-api.open-meteo.com` | Search city/neighborhood coordinates | Search queries transmitted |
| **Google Fonts** | `https://fonts.googleapis.com`, `fonts.gstatic.com` | Outfit, Plus Jakarta Sans, JetBrains Mono | IP address sent to Google CDN |
| **YouTube** | `https://www.youtube.com/embed/...` | Embedded educational air quality videos | Third-party cookies/trackers by YouTube/Google |
| **Regulatory Portals** | CPCB, CAQM, DPCC, WHO, NASA, Copernicus | Referenced documentation links | Navigational only |

---

## 7. Action Plan for Phase 1 (Fixes F1–F10)

1. **F1:** Add root `LICENSE` (MIT, Akshat Kumar); update `.github/workflows` to trigger on `push` and `pull_request`; replace static test badge with live GitHub Actions badge.
2. **F2:** Reconcile `requirements.txt` (remove LightGBM/CatBoost claims or add pinned dependencies); build minimal `api/requirements.txt`; ensure `ml/` is added to `.vercelignore`.
3. **F3:** Standardize canonical naming (`AirFusion` / `airfusion.vercel.app`); replace "WCAG AAA Certified" with "Built with accessibility in mind"; correct "100% Zero Personal Tracking" to accurately disclose third-party API/CDN calls; replace unverified marketing superlatives.
4. **F4:** Verify `api/index.py` statelessness (no SQLite dependency); document that SQLite logging operates in local Streamlit mode only.
5. **F5:** Create shared test vectors in `tests/golden/*.json` (AQI breakpoints, Gaussian plume, Köhler equation, Ångström exponent, ventilation coefficient); add Python pytest and Node.js test runners in CI.
6. **F6:** Implement explicit US EPA vs Indian CPCB standard toggle; map correct units (CO in $\text{mg/m}^3$ for CPCB vs $\text{ppm}$ for EPA); verify GRAP measures against current CAQM statutory orders.
7. **F7:** Fix cigarette equivalence formula to Berkeley Earth standard; verify alveolar deposition fraction against ICRP guidelines; add "Not medical advice" disclaimers.
8. **F8:** Correct satellite data-source attribution for AOD (AERONET/MODIS instead of TROPOMI); label absorption index formula as illustrative.
9. **F9:** Reconcile ML metrics in `reports/metrics.json`; replace hardcoded values in Model Diagnostics with true baseline and XGBoost performance data.
10. **F10:** Ensure UI and README explicitly state that Vercel serves client-side telemetry and physics engines, with offline-trained ML benchmarks reported transparently.
