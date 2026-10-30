# Changelog (CHANGELOG.md)

All notable changes to the AirFusion codebase on branch `fix/audit-and-cnn` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] - Branch `fix/audit-and-cnn`

### Added
- `AUDIT.md`: Complete Phase 0 architectural audit covering data pipeline, ML models, LSTM status, CI test status, and third-party services.
- `DECISIONS.md`: Structured log of engineering and scientific decisions.
- `CHANGELOG.md`: Detailed file-by-file record of modifications.
- `LICENSE`: MIT License with copyright holder Akshat Kumar.
- `.github/workflows/ci.yml`: Automated CI workflow executing pytest on push and pull request.
- `api/requirements.txt`: Lightweight requirements specification for Vercel serverless function (standard library only).
- `tests/golden/*.json`: Canonical shared test vectors for Gaussian plume, Köhler equation, Ångström exponent, ventilation coefficient, and EPA/CPCB AQI sub-indices.
- `airfusion/src/physics_models.py`: Python metrological model implementations matching client-side equations.
- `airfusion/tests/test_golden_vectors.py`: Pytest suite verifying Python physics models against golden test vectors.
- `tests/verify_js_golden.js`: Node.js test runner validating JavaScript physics against golden test vectors.

### Changed
- `airfusion/LICENSE`: Updated copyright holder to Akshat Kumar.
- `README.md`, `airfusion/README.md`: Replaced static test badge with live GitHub Actions CI badge; replaced fictitious LightGBM/CatBoost benchmark tables with real verified offline metrics (XGBoost, RF, Ridge, PyTorch LSTM, Persistence).
- `.vercelignore`: Added `ml/`, `reports/`, and `scratch/` to prevent training scripts and raw files from bundling into Vercel deployment.
- `public/index.html`: Standardized API code samples to `https://airfusion.vercel.app`; replaced "WCAG AAA Certified" with "Built with accessibility in mind"; replaced "100% Zero Personal Tracking" with truthful privacy statement; labeled telemetry overlays and 3D guardians as simulated educational visuals.
- `airfusion/app/components/cards.py`, `simple_cards.py`, `simple_views.py`, `pages/0_Platform_Intro.py`: Removed "Pixar" brand references and unverified accessibility certificates.
- `api/index.py`: Added explicit architectural docstrings affirming stateless read-only operation with zero database dependencies.
- `README.md`, `airfusion/README.md`: Added serverless hygiene note documenting that SQLite logging is scoped strictly to local Streamlit execution.
- `reports/metrics.json`: Canonical machine learning report containing multi-model benchmarks, multi-horizon evaluations (1h, 6h, 24h, 72h) against Persistence and Seasonal-Naive baselines, measured inference latency, and CAMS atmospheric reanalysis target disclosures.
- `public/index.html`:
  - Added explicit CPCB (India NAQI) vs US EPA (40 CFR Part 58) standard toggle in Sub-Index Resolver with official breakpoint tables and dynamic pollutant units (CO in mg/m³ for CPCB, ppm for EPA; NO2/SO2/O3 in ppb for EPA).
  - Tied 3D Guardian mood reactivity directly to the CPCB NAQI scale (Good/Satisfactory ≤100, Moderate 101–200, Poor 201–300, Severe >300).
  - Updated CAQM GRAP Matrix statutory authority citations to CAQM Direction No. 80 / Order F. No. 120017/GRAP/2021/CAQM (October 2024 active schedule) linked to `caqm.nic.in`.
  - Fixed health model cigarette equivalence to the Berkeley Earth rule $(PM_{2.5} / 22) \times (t / 24h) \times (V_E / V_{\text{rest}})$, replacing flawed `totalInhaledMass / 22.0`.
  - Corrected pulmonary deposition labels to distinguish alveolar (~20-30%, slow clearance) from tracheobronchial (~10%, 24-48h mucociliary clearance) based on ICRP Publication 66.
  - Added "Not medical advice" notices to personal exposure cards.
  - Corrected Satellite AOD data attribution to AERONET Sun-Photometer & MODIS (440nm, 870nm), clarified Sentinel-5P TROPOMI UVAI (354/388nm), and labeled AAI formula as illustrative absorption proxy.
  - Updated Model Diagnostics UI to display verified multi-model and multi-horizon benchmarks from `reports/metrics.json`, replacing fabricated LightGBM/CatBoost metrics.
- `airfusion/tests/test_ui.py`: Optimized `is_server_running` HTTP health check with result caching and a 0.5s timeout, reducing test suite startup from 48 seconds to instant.
- `README.md`, `airfusion/README.md`: Reconciled 24h vs 72h lead horizons, added multi-horizon evaluation table, corrected Berkeley Earth formula, documented physical ground station truth gap and OpenAQ v3 API key requirement, and affirmed production client-side vs local Streamlit architecture.

### Phase 2: CNN Photo AQI Fusion Module (Behind `ENABLE_CNN_FUSION`)
- `DATA_SOURCES.md`: License analysis and documentation for PM25Vision (CC-BY-4.0), Air Pollution Image Dataset from India and Nepal (CC0-1.0), Dhaka Smartphone PM2.5 Dataset (CC-BY-4.0), and HVAQ Dataset.
- `TRAINING.md`: End-to-end instructions for dataset acquisition, preprocessing, MobileNetV3 fine-tuning, and ONNX export.
- `ml/README.md`: Architectural documentation for atmospheric vision modeling and residual fusion.
- `ml/dataset.py`: PyTorch dataset loader with perceptual hashing (`dHash`) deduplication and zero-leakage station/time-aware partitioning.
- `ml/model.py`: MobileNetV3-Small vision backbone with heteroscedastic uncertainty regression head and OOD gating.
- `ml/train.py`: Offline training pipeline with early stopping and evaluation metric tracking.
- `ml/export_onnx.py`: Quantization and export script targeting `public/models/airfusion_cnn_v1.onnx` (<10 MB).
- `ml/notebooks/Train_AirFusion_CNN.ipynb`: Colab-ready notebook for GPU training and one-click ONNX export.
- `ml/tests/test_cnn_pipeline.py`: Pytest suite (5 passed) covering transforms, hashing, station-day partitioning, model forward pass, and residual fusion limits.
- `public/js/photo-aqi.js`: Client-side browser module loading `onnxruntime-web`, offscreen canvas 224x224 extraction, residual fusion, and Mode C fallback.
- `public/index.html`: Integrated `window.ENABLE_CNN_FUSION = false` flag, external script inclusion, sidebar navigation hook, and page routing.
- `tests/test_cnn_fusion_flag.js`: Node.js test suite (8 passed) validating flag gating, Mode C fallback, and Data & Credits citations.
- `.github/workflows/ci.yml`: Integrated `ml/tests/` pytest and `test_cnn_fusion_flag.js` into CI workflow.

### Simple Mode Polish, Interactivity & Integrity
- `public/index.html`:
  - Resolved Temporal Dead Zone `ReferenceError` on `WMO_WEATHER_CODES` by restructuring declaration order above `state`, unblocking all client-side JavaScript execution.
  - Upgraded `speakVoice` speech synthesis helper to safely catch errors, handle missing voices, and eliminate blocking browser alert dialogs.
  - Upgraded `renderHomeSimple`: added 6 Criteria Pollutants Dials (PM2.5, PM10, NO2, SO2, O3, CO) and 4 Weather Vitals cards (Temperature, Humidity, Wind & Dispersion, UV Index); persisted Aero AI Chatbot history across re-renders; added interactive checklist toggling to Departure Kit; added search query input and instant filtering to Everyday Air Decoder.
  - Upgraded `renderLiveTrackingSimple`: replaced 2-card placeholder with full Live Sentry Hub featuring big animated Clean Air Dial, 6 Pollutant Family Cards with WHO guideline comparison bars and clickable deep-dive inspectors, real-time atmospheric vitals, and working CSV telemetry download.
  - Upgraded `renderSafePlanSimple`: replaced static text with dynamic quantitative dosimetric inhalation and cigarette equivalence calculations tailored to age, airway sensitivity, and activity tier.
  - Upgraded `renderTrendsSimple`: added interactive day selection to 7-Day Clean Air Outlook Calendar with dynamic Day Briefing panel.
  - Upgraded `renderModelInsightsSimple`: replaced unverified 99.4% accuracy claim with empirical XGBoost benchmarks (20.47 µg/m³ Test MAE) and added interactive Clean Air Physics Simulator.
  - Upgraded `renderCityCompareSimple`: expanded leaderboard to display all 14 monitoring cities with live/calibrated AQI, PM2.5, rank medals, and seamless "Visit City" switching.
- Upgraded `renderHomeSimple`: added Executive Family Clean Air Command Center Hero Hub at the top of the Home page, providing an immediate real-time situation room with big numeric AQI, WHO health guideline comparison, dynamic weather snapshot, instant city switcher, and 4 tactile rapid command launcher cards (`My Safe Outdoor Plan`, `Live Sentry`, `24h Trends`, `Guardians Quest & Safety Lab`) ensuring full parity with sidebar navigation.
  - Integrated 3D Cartoon Guardians Sentry Showcase directly inside the Home Command Center, fixed hardcoded absolute image paths (`/assets/images/...` to relative `assets/images/...`) across panoramic dioramas, mascot avatars, and storybook chapters, added multi-tier error fallbacks and an embedded high-definition animated SVG diorama fallback, and added an interactive Clean Air Bubble Shield toggle button (`🛡️ Activate Clean Air Bubble`) with speech synthesis.
