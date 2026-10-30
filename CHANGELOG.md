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

### Changed
- `airfusion/LICENSE`: Updated copyright holder to Akshat Kumar.
- `README.md`, `airfusion/README.md`: Replaced static test badge with live GitHub Actions CI badge; replaced fictitious LightGBM/CatBoost benchmark tables with real verified offline metrics (XGBoost, RF, Ridge, PyTorch LSTM, Persistence).
- `.vercelignore`: Added `ml/`, `reports/`, and `scratch/` to prevent training scripts and raw files from bundling into Vercel deployment.
