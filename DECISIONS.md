# AirFusion Architecture & Implementation Decisions Log (DECISIONS.md)

This log records every architectural, engineering, and data-integrity decision made on branch `fix/audit-and-cnn`.

---

## Decision Index

| ID | Date | Category | Topic | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **D01** | 2026-10-30 | Branching | Branch Isolation | Created dedicated branch `fix/audit-and-cnn` off `main`. Strictly no pushes to `main` and no production deployments. |
| **D02** | 2026-10-30 | Audit | Baseline Ground Truth | Documented in `AUDIT.md` that production is client-side static HTML/JS querying Open-Meteo, while ML models trained offline are not deployed on Vercel. Test baseline recorded as 54 passed, 8 skipped (62 total). |
| **D03** | 2026-10-30 | Fix F1 | Licensing & CI Verification | Added MIT LICENSE (Akshat Kumar) at root and updated airfusion/LICENSE. Created `.github/workflows/ci.yml` targeting push and pull_request. Replaced static 60/60 badge with GitHub Actions badge. |
| **D04** | 2026-10-30 | Fix F2 | Truthful Dependencies & Serverless Isolation | Corrected README ML architecture to reflect true trained models (Ridge, RF, XGBoost, PyTorch LSTM) and real test metrics, removing uninstalled LightGBM/CatBoost claims. Created `api/requirements.txt` with zero external dependencies to prevent heavy packages on Vercel. Added `ml/`, `reports/`, and `scratch/` to `.vercelignore`. |
| **D05** | 2026-10-30 | Fix F3 | Truthful Claims & Canonical Domain | Standardized canonical domain to `https://airfusion.vercel.app`. Replaced unverified "WCAG AAA Certified" claim with "Built with accessibility in mind". Replaced "100% Zero Personal Tracking" with truthful disclosure of client-side requests to public weather APIs. Removed unverified marketing superlatives ("Pixar-grade", "institutional-grade") and labeled video telemetry overlays and guardian animations as simulated educational visualizations. |
| **D06** | 2026-10-30 | Fix F4 | Serverless Statelessness Verification | Verified `api/index.py` is purely stateless, free of SQLite dependencies, and performs zero disk writes. Explicitly documented that persistent telemetry logging operates solely in the local Streamlit application. |
