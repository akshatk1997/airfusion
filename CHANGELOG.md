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
