# Changelog (CHANGELOG.md)

All notable changes to the AirFusion codebase on branch `fix/audit-and-cnn` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] - Branch `fix/audit-and-cnn`

### Fixed
- `public/index.html`:
  - **Home Command Center**: Resolved quote-escaping inline string syntax errors by introducing dedicated `playGuardianVoice('aero')`, `playStoryChapterVoice(idx)`, and `playCityAudioSummary(city)` helpers. Added floating `guardian-speech-toast` caption bubble providing instant visual confirmation of voice synthesis even when browser audio is blocked or muted. Enhanced `changeCity(city)` with zero-latency synchronous telemetry binding and green action confirmation toast (`showAirFusionToast`).
  - **Guardians Tour & Eco Quest**: Integrated the comprehensive 5-module platform tour into Simple Mode: (1) 4-Guardian mission dossier with live voice briefings and superpowers, (2) 3-Chapter illustrated Clean Air Family Storybook with chapter navigation and audio narration, (3) Haven's Clean Air Sanctuary Simulator and NASA Plant Doctor with room switcher, purifier mode controller, plant counter, window shield toggle, and live purity gauge, (4) Aero's Adventure Quiz with streaks and detailed explanations, and (5) Hero Badge Trophy Case with 5 unlockable badges. In Technical Mode, preserved systems architecture dossier and toxicokinetics specifications while adding an interactive CADR room clearance workbench.
  - **City Comparison Radar**: Built an interactive multi-axis SVG Environmental Radar Chart plotting 5 atmospheric dimensions (PM2.5 Purity, Wind Dispersion, Inversion Relief, Gas Buffer, Airshed Relief) with head-to-head comparative analysis. Replaced hardcoded "75" values across cities with 14 calibrated, realistic regional telemetry baselines. Added region filter pills (North, South & West, East, Global), sort dropdown (Cleanest First, Highest AQI First, Alphabetical), real-time search input, and responsive "Visit & Bind Sentry" buttons.
  - **Verified News & Videos**: Isolated article topic filters (`ns.topicFilter`) and video topic filters (`ns.videoTopicFilter`) to prevent empty state bugs when switching tabs. Added video fail-safe links to authoritative sources, live wire refresh pulse with toast notification, situational telemetry alerts calibrated to active city, and verified 18 regulatory source registries.
- **Performance & Deployment Optimization**:
  - Compressed all 19 high-resolution images in `public/assets/images/` using progressive JPEG compression (quality 82, Lanczos resampling), reducing asset weight from 15.79 MB to 3.54 MB (-77.6% savings) for instant mobile loading and friction-free Vercel builds.
  - Mirrored `index.html`, `assets/`, and `js/` at project root to guarantee instant static resolution under all Vercel root and output directory configurations.

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
- `vercel.json`: Added production caching rules (`Cache-Control: public, max-age=31536000, immutable` for `/assets/**`), HTTP security headers (`nosniff`, `SAMEORIGIN`, `strict-origin-when-cross-origin`), and explicit `/api/(.*)` serverless routing to `api/index.py` with 15s max execution duration.

## [Brand & Repository Harmonization] - 2026-10-30
### Fixed
- `js/photo-aqi.js` & `public/js/photo-aqi.js`: Replaced hardcoded local file links containing legacy project path names with canonical web GitHub links (`https://github.com/akshatk1997/airfusion/blob/main/TRAINING.md`).
- Verified across all 11,000+ lines in `index.html`, `public/index.html`, `api/index.py`, `ml/`, and documentation that zero references to `airguard` or `airgd` remain in tracked files.
- Synchronized repository changes to both `fix/audit-and-cnn` and `main` branches on GitHub.

## [Eco-Specific Logo & Floating Semi-Round Dual-AI Hub] - 2026-10-30
### Added
- **Eco-Specific Biophilic Logo**: Re-engineered the brand emblem across `assets/images/airfusion_shield_logo.svg`, `public/assets/images/airfusion_shield_logo.svg`, `favicon.svg`, `public/favicon.svg`, and inline header/sidebar SVGs. The new emblem features an organic biophilic bio-canopy pebble hull, sculpted botanical leaf wing with glowing chlorophyll veins, tropospheric laminar airflow ribbon, central bio-atmospheric dewdrop convergence lens, and radiant solar photosynthesis core.
- **Floating Semi-Round Dual-AI Hub (`#floatingAiLauncher` & `#floatingAiWindow`)**:
  - Persistent floating launcher in the bottom-right corner with pulse indicator and semi-round pill form factor.
  - Semi-round modal with blurred backdrop, custom header, motto callout strip, decoupled conversation thread, quick prompt suggestions, and input bar.
  - **Decoupled Mode Motos & Personas**:
    - **Simple Mode**: *Aero AI Family Companion* — "Guarding your family's health through clear, actionable outdoor answers and child-safe air windows." Focused on kids' play windows, mask necessity, air-purifying plants, and home ventilation.
    - **Technical Mode**: *AtmoMetrix AI* — "Providing empirical Gaussian dispersion equations, boundary layer thermodynamic flux, and statutory CAQM/EPA breakpoints." Focused on plume dispersion math, CPCB/EPA sub-indices, Köhler aerosol hygroscopy, and CAQM GRAP mitigation matrices.
  - **100% Decoupled Memory Guarantee**: Maintains independent state arrays (`simpleAiHistory` vs `techAiHistory`) that dynamically switch upon mode toggling without memory cross-contamination.
  - Mode-isolated history clearing via `clearCurrentAiHistory()`.
  - Comprehensive interactive test suite verifying strict memory decoupling and persona switching (`scratch/test_floating_ai_interactive.js`).


## [Premium Botanical Aesthetic Logo from User Reference] - 2026-10-30
### Added & Updated
- **Faithful Botanical Sprig Emblem Engineering**: Digitized the 5-leaf botanical twig from the user's uploaded reference image (`media_1793379033595_ce8a9c8a.jpg`) into a high-precision, scalable vector SVG artwork.
  - Features 5 organic Bezier-curved leaves (bottom-right pointing -18°, mid-right pointing 12°, top-right pointing 42°, top-center upright 78°, and left pointing 110°) emerging from a curved central stem with cut joint node.
  - Styled with multi-stop botanical chlorophyll gradients (`#2D7A38` to `#81C784`, `#A5D6A7`, `#9CCC65`) and specular gloss crest highlights (`#B4F588`, `#D4FC79`).
  - Housed on a luxury dark obsidian/evergreen squircle medallion (`#1A201E` to `#0C100F`, `rx="26"`) with precision bio-rim border (`#34D399` / `#10B981` / `#38BDF8`), preserving high contrast against the app's warm background while matching the dark aesthetic of the user's reference.
- **Universal Logo Replacement**:
  - Replaced all 6 primary SVG files: `public/assets/images/airfusion_shield_logo.svg`, `assets/images/airfusion_shield_logo.svg`, `public/assets/images/airfusion_logo.svg`, `assets/images/airfusion_logo.svg`, `airfusion/app/assets/images/airfusion_logo.svg`, and `airfusion/app/assets/images/airfusion_shield_logo.svg`.
  - Replaced all 3 favicon files: `public/favicon.svg`, `favicon.svg`, and `airfusion/app/assets/images/favicon.svg`.
  - Updated inline SVGs in `index.html` and `public/index.html` for the sidebar brand-icon, topbar mini-brandmark, and the `<link rel="icon">` base64 data URI.
- **Verification**:
  - Full golden vector tests (`tests/verify_js_golden.js`, 83/83 passed).
  - CNN module tests (`tests/test_cnn_fusion_flag.js`, 8/8 passed).
  - All page renders & interactive action handlers (`scratch/test_all_renders.js`, 18/18 renders, 26/26 handlers passed).
  - Floating semi-round Dual-AI tests (`scratch/test_floating_ai_interactive.js`, 7/7 passed).
  - Python test suite (`python -m pytest airfusion/tests ml/tests`, 64/64 passed, 8 skipped).


## [Comprehensive Dual-Mode Landing Page & Welcome Experience] - 2026-11-26
### Added & Updated
- **Dedicated Dual-Mode Landing Page Engine (`renderLandingSimple` & `renderLandingTechnical`)**:
  - **Simple Mode Experience**:
    - **Atmospheric Family Sanctuary Hero**: Master botanical branding badge, headline "Breathe Freely. Plan Confidently. Protect Every Breath", live atmospheric compass HUD with active city selector, dynamic AQI category badge, and 1-click audio story summary.
    - **Philosophy & Value Proposition Cards**: 4 core cards contrasting raw lagging scores with AirFusion's human-first guidance (Zero Guesswork, Clean Sunshine Windows, Personalized Inhaled Dose, Peaceful Indoor Fortress).
    - **Interactive "Clean Air Window Finder" Mini-Widget**: Instant calculation of safe hours and gear for Toddler & Playground Play 🛴, Morning Cardio 🏃, City Cycling & Commute 🚴, and Senior Evening Walks 🚶.
    - **Guardian Sentinels Character Showcase**: Interactive character cards for Aero, Flash, Nova, and Haven with voice playback buttons (`playGuardianVoice`).
    - **8 Intelligence Modules Showcase Grid**: Direct interactive launch cards for Home Command Center, Safe Outdoor Plan, Live Tracking & Sentry, Trends & Analytics, Model Diagnostics, Guardians Tour & Quest, City Comparison Radar, and Verified News.
    - **CTA Finale**: Eco-sanctuary action banner inviting families to enter the command center, explore city comparison, or chat with Aero AI.
  - **Technical Mode Experience**:
    - **Atmospheric Command Hero**: CAAQMS sentry array badge, headline "Autonomous Atmospheric Intelligence & Mesoscale Physics", live boundary layer microphysics HUD (PBLH, Dew point, ventilation coefficient $V_c = H_{mix} \cdot U_{10}$, inversion regime status), and audio briefing.
    - **4 Mathematical Architecture Pillars**: Detailed technical cards for Data Assimilation, Gradient-Boosted ML (XGBoost Test MAE 20.47 µg/m³), Gaussian Plume Dispersion Kinetics, and Clinical Inhalation Dosimetry (ICRP 66).
    - **Stateless Edge Runtime Showcase**: Real-time telemetry inspector, Vercel Serverless latency verification, and regulatory scale documentation.
    - **Technical Sentry Subsystems Directory**: Direct links to all mathematical modeling engines.
- **Routing & Navigation Integration**:
  - Added `✨ Welcome & Landing` (`#nav-landing`) as the top-most item in the sidebar navigation menu.
  - Connected sidebar brand link and collapsed topbar brand mark to navigate smoothly to `landing`.
  - Configured initial state to launch into `currentPage: 'landing'` while preserving seamless 1-click access to the full live Home Command Center.
  - Aliased `renderIntroSimple` and `renderIntroTechnical` to the landing page engine for full backward compatibility.
- **Testing & Verification**:
  - Added `scratch/test_landing_interactive.js` verifying initial state, simple/technical renders, activity switching, and navigation transitions.
  - Node golden vector tests (83/83 passed).
  - CNN module flag tests (8/8 passed).
  - Full view & action handler suite (18/18 renders, 26/26 handlers passed).
  - Floating semi-round Dual-AI tests (7/7 passed).
  - Python test suite (`pytest airfusion/tests ml/tests`, 64/64 passed, 8 skipped).


## [Standalone Product Landing Page & Dedicated 'Go Live' Separation] - 2026-11-26
### Added & Updated
- **Physical Decoupling of Product Landing Page & Main Work Workspace**:
  - Implemented standalone `#standaloneLandingPage` container completely detached from the internal `#app-root` dashboard layout.
  - On initial visit, internal sidebars, place search bars, and complex working tools are hidden, providing a clean, distraction-free product landing experience.
  - Dedicated sticky top navigation bar with botanical brand mark, anchor links (`What It Is`, `Work Modules`, `Activity Finder`, `Eco Guardians`, `Science & Trust`), dynamic Simple/Technical view mode toggle, and a glowing `🚀 Go Live` call-to-action button.
- **Dual-Workspace Controller & Transition Mechanics (`goLive` & `exitToLanding`)**:
  - `goLive(targetPage)`: Transitions from the standalone landing page into the live working tool (`#app-root`), mounts the requested module (defaulting to Home Command Center), highlights the corresponding sidebar navigation item, and scrolls to top.
  - `exitToLanding()`: Smoothly hides the working dashboard and restores the standalone product landing page.
  - Main work page topbar now features a persistent `🌿 Product Overview` button, and the sidebar features a `🌿 Exit to Product Landing` action for instant round-trip navigation.
- **Verification & Selenium End-to-End Validation**:
  - Closed block scope and explicitly bound `window.goLive`, `window.exitToLanding`, `window.renderLandingPage`, and `window.selectLandingActivity` to ensure error-free global hoisting across all browsers.
  - Pre-rendered static landing HTML directly into `#standaloneLandingContent` in both `index.html` and `public/index.html`, eliminating FOUC and guaranteeing instant presentation.
  - Linked `setViewMode(mode)` to re-render `#standaloneLandingContent` dynamically, enabling real-time toggling between Simple and Technical showcase modes on the landing page.
  - Verified in headless Chrome via Selenium (`scratch/verify_browser_flow.py`): initial landing display (100% visible, app-root hidden), Go Live click (landing hidden, app-root flex display), Product Overview exit click (landing restored, app-root hidden), and Simple/Technical mode switching.
  - Transition mechanics suite (`scratch/test_standalone_transition.js` passed 100%).
  - Full view & action handler suite (18/18 renders, 26/26 handlers passed).
  - Floating semi-round Dual-AI tests (7/7 passed).
  - Python test suite (64/64 passed, 8 skipped).


## [Professional SaaS-Level Landing Page & Complete Platform A-to-Z Showcase] - 2026-11-26
### Added & Enhanced
- **Enterprise SaaS Design System & Typography**:
  - Replaced legacy landing styles with a modern SaaS visual design system (Linear/Vercel/Stripe aesthetic) featuring radial background mesh glows, refined cards with subtle 1px border glows, interactive badge pills, high-contrast CTA buttons, live ping indicators, animated pulse elements, and responsive layout across desktop, tablet, and mobile.
  - Sticky glassmorphic SaaS topbar (`.saas-nav`) with botanical brand mark, anchor navigation links (`Platform`, `A-Z Modules`, `Activity Engine`, `Eco Guardians`, `Science & Standards`, `FAQ`), dynamic Simple/Technical mode switcher, and glowing `🚀 Launch Platform (Go Live)` button.
- **Interactive Live SaaS Console Sandbox**:
  - Integrated macOS browser chrome frame with live city selector dropdown (`Delhi`, `Mumbai`, `Bengaluru`, `Kolkata`, `Chennai`, `Hyderabad`, `Pune`, `London`, `New York`, `Tokyo`, `Paris`), real-time AQI meter with animated gradient bar and category indicator, 6 criteria pollutants matrix ($PM_{2.5}, PM_{10}, NO_2, SO_2, CO, O_3$), synoptic boundary layer metrics ($T, T_d, z_{PBL}, V_C$), and direct workspace bridge link.
- **Proof & Architecture Metrics Strip**:
  - Added 4-card metric strip: 14 Monitored Metropolises, 6 Criteria Pollutants Analyzed, LightGBM + XGBoost Multi-Horizon Forecasting, and 100% Stateless Edge Compute with zero tracking cookies.
- **Interactive Clean Air Activity Window Finder**:
  - Segmented control tabs for toddlers, runners, cyclists, and seniors that dynamically calculate safe exposure duration, recommended hour window, minute ventilation ($V_E$), and mask/HEPA advice based on active city telemetry.
- **Complete A-to-Z 8 Core Work Modules Bento Grid**:
  - 8 interactive bento cards showcasing every module in the application with direct 1-click workspace launchers:
    1. Home Command Center (`goLive('home')`)
    2. Safe Outdoor Planner (`goLive('safe_plan')`)
    3. Live Tracking & Sensor Array (`goLive('live_tracking')`)
    4. Multi-Horizon Trends & Forecast (`goLive('trends')`)
    5. Model Insights & Explainability (`goLive('model_insights')`)
    6. Guardians Tour & Eco Quest (`goLive('safety_quest')`)
    7. City Comparison Radar (`goLive('compare')`)
    8. Verified News, Alerts & Telemetry Wire (`goLive('news')`)
- **Eco-Guardians Sentry Roster & Audio Briefings**:
  - 4 Guardian profile cards for Aero, Haven, Zephyr, and Terra with superpowers, mission directives, and interactive audio briefing buttons (`playGuardianVoice(...)`) that trigger real-time speech synthesis and visual caption toasts.
- **Scientific Foundations & Metrological Architecture**:
  - 4 deep-dive cards covering Gaussian Plume Dispersion ($C(x,y,z)$), Köhler aerosol growth, statutory CPCB NAQI vs EPA 40 CFR Part 58 breakpoints, CAQM Direction No. 80 GRAP Matrix, Berkeley Earth toxicokinetics, and stateless REST API code workbench.
- **Interactive SaaS FAQ Accordion & Final Conversion CTA**:
  - 5-item collapsible FAQ list covering telemetry sources, privacy, mode capabilities, ML models, and health formulations.
  - High-converting dark glassmorphic CTA banner with glowing emerald border and dual action buttons.
  - Multi-column SaaS directory footer with product links, science docs, legal disclosures, and MIT license.
- **Verification & Deployment**:
  - Verified in headless Chrome via Selenium with 9/9 automated checks passing and 0 console errors.
  - 83/83 golden vector physics assertions passed.
  - 8/8 CNN module tests passed.
  - 18/18 page renders and 26/26 action handlers passed.
  - 7/7 floating dual-AI popup isolation tests passed.
  - 64/64 pytest tests passed (8 skipped).
  - Dual-mirror integrity: `index.html` and `public/index.html` remain 100% byte-for-byte identical.

## [Creative Atmospheric Animations, Radial Gauges & Performance Optimization] - 2026-11-26
### Added & Enhanced
- **Tropospheric Ambient Aurora (`.saas-aurora-bg`)**:
  - Built an ambient 16-second drifting atmospheric radial glow behind the hero (`@keyframes saasAuroraDrift`), tinting emerald in Simple Mode and cyan/mint in Technical Mode to simulate real-time planetary tropospheric air currents.
- **Organic Breathing Eco-Guardian Avatars (`.saas-guardian-avatar`)**:
  - Engineered breathing scale and shadow pulse keyframe animations (`@keyframes saasAvatarBreathe`) with staggered rhythm offsets across Aero (0s), Haven (1.1s), Zephyr (2.2s), and Terra (3.3s) for an organic, lifelike sanctuary sentry experience.
- **Dynamic Animated SVG Radial AQI Gauge (`.saas-gauge-visual`)**:
  - Added a circular SVG gauge in the SaaS Console Sandbox dynamically computing stroke dash offset ($213.6 \times (1 - \text{AQI}/300)$) with real-time severity arc colors (Green $\le 50$, Light Green $\le 100$, Amber $\le 150$, Coral $\le 200$, Crimson $> 200$).
- **Interactive Activity Exposure Visualizer**:
  - Integrated dynamic dosage exposure meter in the Clean Air Activity Finder calculating the percentage of daily allowable particulate burden based on active city PM2.5 concentrations.
- **Ambient CTA Breathing Pulse (`.saas-btn-primary`)**:
  - Added a subtle 4-second emerald ambient pulse glow (`@keyframes saasCtaAmbient`) to primary conversion action buttons.
- **Bento Grid Light Shimmer & GPU Lift**:
  - Implemented light shimmer sweep on card hover (`.saas-bento-card::before`) with GPU-accelerated 6px lift (`translateY(-6px)`).
- **Interactive 1-Click API Snippet Copy**:
  - Added `copyApiSnippet(btn)` helper providing instantaneous "✓ Copied!" visual feedback and fallback notification.
- **Animated FAQ Chevron Indicator**:
  - Added CSS rotation transition on `.saas-faq-chevron` when `<details open>` is triggered.
- **CSS Compositing & Rendering Optimization**:
  - Added `contain: layout style;` and `transform: translateZ(0)` on animated cards and avatars to prevent layout reflows and guarantee 60fps rendering performance.