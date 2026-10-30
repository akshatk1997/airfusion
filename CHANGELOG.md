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
