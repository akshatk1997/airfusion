# AirFusion Architecture & Implementation Decisions Log (DECISIONS.md)

This log records every architectural, engineering, and data-integrity decision made on branch `fix/audit-and-cnn`.

---

## Decision Index

| ID | Date | Category | Topic | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **D01** | 2026-10-30 | Branching | Branch Isolation | Created dedicated branch `fix/audit-and-cnn` off `main`. Strictly no pushes to `main` and no production deployments. |
| **D02** | 2026-10-30 | Audit | Baseline Ground Truth | Documented in `AUDIT.md` that production is client-side static HTML/JS querying Open-Meteo, while ML models trained offline are not deployed on Vercel. Test baseline recorded as 54 passed, 8 skipped (62 total). |
| **D03** | 2026-10-30 | Fix F1 | Licensing & CI Verification | Added MIT LICENSE (Akshat Kumar) at root and updated airfusion/LICENSE. Created `.github/workflows/ci.yml` targeting push and pull_request. Replaced static 60/60 badge with GitHub Actions badge. |
