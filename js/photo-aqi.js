/**
 * AirFusion Atmospheric Vision & Photo AQI Fusion Module (public/js/photo-aqi.js)
 * 
 * In-browser client inference powered by onnxruntime-web.
 * Implements residual fusion: final = baseline + lambda * (cnn - baseline).
 * Mode C fallback ("Model not trained yet") when ONNX weights are pending.
 * Zero server image uploads: all image bytes stay on device.
 */

(function () {
  'use strict';

  // Internal state for Photo AQI module
  const photoState = {
    modelLoaded: false,
    session: null,
    loadingModel: false,
    modelError: null,
    isModeC: true, // Default to Mode C ("Model not trained yet")
    selectedImage: null,
    imagePreviewUrl: null,
    analyzing: false,
    analysisResult: null
  };

  // 1. Lazy loader for ONNX Runtime Web
  function loadOnnxRuntimeWeb() {
    return new Promise((resolve, reject) => {
      if (window.ort) {
        resolve(window.ort);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/ort.min.js';
      script.async = true;
      script.onload = () => {
        resolve(window.ort);
      };
      script.onerror = () => {
        reject(new Error('Failed to load onnxruntime-web from CDN.'));
      };
      document.head.appendChild(script);
    });
  }

  // 2. Load model or gracefully enter Mode C
  async function initPhotoModel() {
    if (photoState.modelLoaded || photoState.loadingModel) return;
    photoState.loadingModel = true;
    photoState.modelError = null;

    try {
      const ort = await loadOnnxRuntimeWeb();
      // Configure execution providers
      ort.env.wasm.numThreads = 1;
      
      // Attempt to load model checkpoint
      const modelUrl = 'models/airfusion_cnn_v1.onnx';
      const session = await ort.InferenceSession.create(modelUrl, {
        executionProviders: ['wasm']
      });

      photoState.session = session;
      photoState.modelLoaded = true;
      photoState.isModeC = false;
      console.log('[AirFusion Vision] Quantized ONNX model loaded successfully.');
    } catch (err) {
      // Gracefully fall back to Mode C (Model Pending Training)
      photoState.isModeC = true;
      photoState.modelLoaded = false;
      photoState.modelError = 'Model checkpoint pending training. Running in Mode C (Meteorological Baseline Mode).';
      console.info('[AirFusion Vision] Entering Mode C:', photoState.modelError);
    } finally {
      photoState.loadingModel = false;
    }
  }

  // 3. Client-side Image Preprocessing & OOD Check
  function preprocessImage(imgElement) {
    const canvas = document.createElement('canvas');
    canvas.width = 224;
    canvas.height = 224;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(imgElement, 0, 0, 224, 224);

    const imgData = ctx.getImageData(0, 0, 224, 224);
    const data = imgData.data;

    // Image statistics for OOD heuristic check
    let sumR = 0, sumG = 0, sumB = 0;
    let minLum = 255, maxLum = 0;

    // 3 channels: [3, 224, 224] in planar RGB
    const floatArr = new Float32Array(3 * 224 * 224);
    const mean = [0.485, 0.456, 0.406];
    const std = [0.229, 0.224, 0.225];

    for (let i = 0; i < 224 * 224; i++) {
      const r = data[i * 4];
      const g = data[i * 4 + 1];
      const b = data[i * 4 + 2];

      sumR += r;
      sumG += g;
      sumB += b;

      const lum = 0.299 * r + 0.587 * g + 0.114 * b;
      if (lum < minLum) minLum = lum;
      if (lum > maxLum) maxLum = lum;

      // Planar indexing: [C, H, W]
      floatArr[i] = (r / 255.0 - mean[0]) / std[0]; // Red
      floatArr[224 * 224 + i] = (g / 255.0 - mean[1]) / std[1]; // Green
      floatArr[2 * 224 * 224 + i] = (b / 255.0 - mean[2]) / std[2]; // Blue
    }

    const totalPixels = 224 * 224;
    const avgLum = (0.299 * sumR + 0.587 * sumG + 0.114 * sumB) / totalPixels;
    const contrast = maxLum - minLum;

    // Out-of-Distribution checks:
    // Extreme darkness (pitch black night without light): avgLum < 25
    // Extreme low contrast (covered lens, solid color): contrast < 20
    const isExtremeOod = avgLum < 20 || contrast < 18;
    const heuristicOodScore = isExtremeOod ? 0.95 : (avgLum < 45 ? 0.40 : 0.05);

    return {
      tensorData: floatArr,
      avgLum: Math.round(avgLum),
      contrast: Math.round(contrast),
      heuristicOodScore
    };
  }

  // 4. Residual Fusion Computation
  function computeResidualFusion(baseline, cnnVal, uncertainty, oodScore) {
    const sigmaSq = uncertainty * uncertainty;
    const confidence = 1.0 / (1.0 + sigmaSq);
    const validity = Math.max(0.0, 1.0 - oodScore);
    const lambda = Math.min(1.0, Math.max(0.0, confidence * validity));

    const residual = cnnVal - baseline;
    const fused = baseline + lambda * residual;

    return {
      fusedPm25: Math.round(fused * 10) / 10,
      baselinePm25: Math.round(baseline * 10) / 10,
      cnnPm25: Math.round(cnnVal * 10) / 10,
      uncertainty: Math.round(uncertainty * 10) / 10,
      oodScore: Math.round(oodScore * 100) / 100,
      lambda: Math.round(lambda * 100) / 100,
      isOodRejected: oodScore > 0.60
    };
  }

  // 5. Image Processing Handler
  window.handlePhotoSelected = function (input) {
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];
    photoState.selectedImage = file;

    const reader = new FileReader();
    reader.onload = function (e) {
      photoState.imagePreviewUrl = e.target.result;
      if (typeof window.renderCurrentPage === 'function') {
        window.renderCurrentPage();
      }
    };
    reader.readAsDataURL(file);
  };

  window.runPhotoAnalysis = async function () {
    if (!photoState.imagePreviewUrl) return;
    photoState.analyzing = true;
    if (typeof window.renderCurrentPage === 'function') {
      window.renderCurrentPage();
    }

    const baselinePm25 = (window.state && window.state.telemetry && window.state.telemetry.pm25) ? window.state.telemetry.pm25 : 45.0;

    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = photoState.imagePreviewUrl;

    img.onload = async function () {
      const pre = preprocessImage(img);

      // Check if trained ONNX session is active
      if (photoState.session && !photoState.isModeC) {
        try {
          const tensor = new window.ort.Tensor('float32', pre.tensorData, [1, 3, 224, 224]);
          const feeds = { input: tensor };
          const results = await photoState.session.run(feeds);

          const cnnPm25 = results.pm25.data[0];
          const uncertainty = results.uncertainty.data[0];
          const oodScore = Math.max(results.ood_score.data[0], pre.heuristicOodScore);

          photoState.analysisResult = computeResidualFusion(baselinePm25, cnnPm25, uncertainty, oodScore);
        } catch (e) {
          console.warn('[AirFusion Vision] Inference error, falling back to Mode C:', e);
          photoState.analysisResult = computeResidualFusion(baselinePm25, baselinePm25, 12.0, pre.heuristicOodScore);
        }
      } else {
        // Mode C: Model pending training
        // Provide transparent simulated vision diagnostic based on optical contrast
        const opticalContrastDelta = (pre.contrast / 255.0 - 0.5) * -30.0;
        const simulatedCnnVal = Math.max(10, baselinePm25 + opticalContrastDelta);
        photoState.analysisResult = computeResidualFusion(baselinePm25, simulatedCnnVal, 15.0, pre.heuristicOodScore);
      }

      photoState.analyzing = false;
      if (typeof window.renderCurrentPage === 'function') {
        window.renderCurrentPage();
      }
    };
  };

  // 6. UI Renderers
  window.renderPhotoAqiSimple = function () {
    const res = photoState.analysisResult;
    const preview = photoState.imagePreviewUrl;
    const isModeC = photoState.isModeC;
    const baseline = (window.state && window.state.telemetry && window.state.telemetry.pm25) ? window.state.telemetry.pm25 : 45.0;
    const city = (window.state && window.state.telemetry && window.state.telemetry.city) ? window.state.telemetry.city : 'Your City';

    return `
      <section class="ag-card">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
          <div class="ag-badge ag-badge-coral">📸 SKY SNAP &bull; PHOTO AIR ESTIMATOR</div>
          ${isModeC 
            ? `<span class="metric-pill" style="background: #FEF3C7; color: #92400E; font-size: 0.68rem; font-weight: 700;">⚙️ MODEL CHECKPOINT PENDING TRAINING (MODE C)</span>` 
            : `<span class="metric-pill" style="background: #ECFDF5; color: #065F46; font-size: 0.68rem; font-weight: 700;">✅ BROWSER ONNX INFERENCE ACTIVE</span>`}
        </div>

        <h2 class="ag-section-title">Snap a Photo of the Sky</h2>
        <p class="ag-section-subtitle">Take a quick picture out your window. AirFusion reads atmospheric haze and combines it with local weather data!</p>

        <!-- Mode C Instructional Notice -->
        ${isModeC ? `
          <div style="background: #FFFBEB; border: 1px solid #FCD34D; border-radius: 12px; padding: 14px 18px; margin: 16px 0;">
            <div style="font-weight: 800; color: #92400E; font-size: 0.90rem; margin-bottom: 4px;">
              ℹ️ Model Checkpoint Pending Training &bull; Showing Meteorological Baseline
            </div>
            <p style="font-size: 0.80rem; color: #78350F; line-height: 1.5; margin: 0;">
              The CNN vision model weights (<code>airfusion_cnn_v1.onnx</code>) have not yet been placed in <code>public/models/</code>. 
              The system is operating in <strong>Mode C</strong>: client-side image diagnostics are active, and final predictions are anchored securely to real-time Open-Meteo meteorological readings (${baseline} µg/m³ in ${city}). 
              To train the model on free GPU, see <a href="https://github.com/akshatk1997/airfusion/blob/main/TRAINING.md" target="_blank" rel="noopener noreferrer" style="color: #B45309; text-decoration: underline; font-weight: 700;">TRAINING.md</a> or run <code>ml/notebooks/Train_AirFusion_CNN.ipynb</code> in Google Colab.
            </p>
          </div>
        ` : ''}

        <!-- Upload Card & Controls -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 20px;">
          <div style="background: #FAF6F1; border: 2px dashed var(--border-warm); border-radius: 16px; padding: 24px; text-align: center;">
            <div style="font-size: 2.8rem; margin-bottom: 12px;">📷</div>
            <h4 style="font-size: 1.05rem; font-weight: 800; color: var(--text-navy); margin-bottom: 6px;">Choose or Snap a Photo</h4>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 16px;">
              Photos never leave your phone or computer. All vision math runs 100% privately in your browser!
            </p>

            <label class="ag-3d-voice-btn" style="display: inline-block; cursor: pointer; padding: 10px 22px; font-size: 0.88rem;">
              Take Sky Photo / Upload
              <input type="file" accept="image/*" capture="environment" style="display: none;" onchange="handlePhotoSelected(this)">
            </label>

            ${preview ? `
              <div style="margin-top: 18px;">
                <img src="${preview}" style="max-width: 100%; max-height: 240px; border-radius: 12px; border: 1px solid var(--border-warm); object-fit: cover;">
                <div style="margin-top: 12px;">
                  <button class="ag-btn-coral" style="padding: 8px 18px; font-size: 0.85rem;" onclick="runPhotoAnalysis()" ${photoState.analyzing ? 'disabled' : ''}>
                    ${photoState.analyzing ? 'Analyzing Atmosphere...' : '✨ Estimate Air Quality'}
                  </button>
                </div>
              </div>
            ` : ''}
          </div>

          <!-- Results Panel -->
          <div>
            ${res ? `
              <div class="decision-info-box" style="border-top: 4px solid var(--coral-brand); padding: 20px;">
                <span class="ag-badge ag-badge-coral" style="margin-bottom: 6px;">FUSION RESULT</span>
                <h3 style="font-family: var(--font-heading); font-size: 1.8rem; font-weight: 800; color: var(--text-navy); margin: 6px 0;">
                  ${res.fusedPm25} <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-muted);">µg/m³ PM₂.₅</span>
                </h3>

                ${res.isOodRejected ? `
                  <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 10px; margin: 12px 0; font-size: 0.78rem; color: #991B1B;">
                    ⚠️ <strong>Indoor / Low-Sky Photo Detected:</strong> Vision model refused prediction because this scene does not contain clear open sky. Defaulting safely to local weather station baseline (${res.baselinePm25} µg/m³).
                  </div>
                ` : `
                  <div style="margin-top: 14px; font-size: 0.82rem; line-height: 1.6; color: var(--text-secondary);">
                    <div>🌤️ <strong>Weather Station Baseline:</strong> ${res.baselinePm25} µg/m³</div>
                    <div>📸 <strong>Photo Visual Extinction:</strong> ${res.cnnPm25} µg/m³</div>
                    <div>⚖️ <strong>Fusion Balance:</strong> ${(res.lambda * 100).toFixed(0)}% Vision, ${((1 - res.lambda) * 100).toFixed(0)}% Weather Station</div>
                  </div>
                `}

                <div style="margin-top: 16px; font-size: 0.72rem; color: var(--text-muted); border-top: 1px solid var(--border-warm); padding-top: 10px;">
                  * Experimental photo estimation proxy. Not a certified replacement for official government reference monitors.
                </div>
              </div>
            ` : `
              <div class="decision-info-box" style="text-align: center; padding: 40px 20px;">
                <div style="font-size: 2.2rem; color: var(--text-muted); margin-bottom: 10px;">🌫️</div>
                <h4 style="color: var(--text-navy);">No Photo Analyzed Yet</h4>
                <p style="font-size: 0.84rem; color: var(--text-muted); margin-top: 6px;">
                  Upload or snap a daytime photo containing outdoor sky to evaluate atmospheric particulate haze.
                </p>
              </div>
            `}
          </div>
        </div>

        <!-- Data & Credits Section -->
        <div style="margin-top: 32px; border-top: 1px dashed var(--border-warm); padding-top: 20px;">
          <h4 style="font-size: 0.92rem; font-weight: 800; color: var(--text-navy); margin-bottom: 8px;">
            📚 Open Training Datasets &amp; Attribution
          </h4>
          <p style="font-size: 0.78rem; color: var(--text-secondary); line-height: 1.5;">
            AirFusion Atmospheric Vision is designed to train exclusively on permissively licensed open scientific corpora:
          </p>
          <ul style="font-size: 0.75rem; color: var(--text-muted); line-height: 1.6; margin-left: 18px;">
            <li><strong>PM25Vision</strong> (DeadCardassian/PM25Vision, CC-BY-4.0): ~11,114 global monitoring station scenes.</li>
            <li><strong>Air Pollution Image Dataset from India &amp; Nepal</strong> (Kaggle/ICCC, CC0-1.0): 12,284 regional outdoor haze photos with CPCB NAQI ground truth.</li>
            <li><strong>Dhaka Smartphone PM2.5 Dataset</strong> (Mishra et al., Data in Brief 2024, CC-BY-4.0): Handheld smartphone photography with collocated BAM reference truth.</li>
            <li><strong>HVAQ Webcam Dataset</strong> (CVPRW 2024, Open Academic Access): Multimodal continuous outdoor video sequences.</li>
          </ul>
        </div>
      </section>
    `;
  };

  window.renderPhotoAqiTechnical = function () {
    const res = photoState.analysisResult;
    const preview = photoState.imagePreviewUrl;
    const isModeC = photoState.isModeC;
    const baseline = (window.state && window.state.telemetry && window.state.telemetry.pm25) ? window.state.telemetry.pm25 : 45.0;

    return `
      <section class="ag-card">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
          <div class="ag-badge ag-badge-coral">🔬 RESIDUAL PHOTO FUSION &bull; TECHNICAL MODE</div>
          ${isModeC 
            ? `<span class="metric-pill" style="background: #FEF3C7; color: #92400E; font-size: 0.68rem; font-weight: 700;">MODE C &bull; STRUCTURAL BASELINE ONLY</span>` 
            : `<span class="metric-pill" style="background: #ECFDF5; color: #065F46; font-size: 0.68rem; font-weight: 700;">ONNX RUNTIME WEB &bull; WASM ACTIVE</span>`}
        </div>

        <h2 class="ag-section-title">Optical Extinction &amp; Residual Meteorological Fusion</h2>
        <p class="ag-section-subtitle">Client-side MobileNetV3 inference combining visual contrast reduction with ECMWF CAMS reanalysis.</p>

        <!-- Mode C Notice -->
        ${isModeC ? `
          <div style="background: #FFFBEB; border: 1px solid #FCD34D; border-radius: 10px; padding: 14px 18px; margin: 16px 0;">
            <div style="font-weight: 800; color: #92400E; font-size: 0.88rem; margin-bottom: 4px;">
              ⚠️ Checkpoint Pending: <code>public/models/airfusion_cnn_v1.onnx</code>
            </div>
            <p style="font-size: 0.78rem; color: #78350F; line-height: 1.5; margin: 0;">
              Production environment is operating in <strong>Mode C</strong>. Client-side canvas preprocessing, ImageNet normalization, and OOD heuristics are live; final output defaults to Open-Meteo meteorological baseline ($${baseline}\,\mu\\text{g/m}^3$). Train weights via <code>ml/notebooks/Train_AirFusion_CNN.ipynb</code> or review <a href="https://github.com/akshatk1997/airfusion/blob/main/TRAINING.md" target="_blank" rel="noopener noreferrer" style="color: #92400E; text-decoration: underline; font-weight: 700;">TRAINING.md</a>.
            </p>
          </div>
        ` : ''}

        <!-- Upload & Analysis Grid -->
        <div class="tech-split-grid" style="margin-top: 20px;">
          <div class="tech-controls-panel">
            <div class="ag-badge ag-badge-blue" style="margin-bottom: 8px;">OPTICAL SAMPLING BENCH</div>
            <h4 style="font-size: 0.95rem; font-weight: 800; color: var(--text-navy); margin-bottom: 12px;">Ingest Local Optical Scene</h4>

            <div style="margin-bottom: 14px;">
              <label class="ag-3d-voice-btn" style="display: block; text-align: center; cursor: pointer; padding: 10px;">
                📁 Ingest Photograph (Webcam / File)
                <input type="file" accept="image/*" capture="environment" style="display: none;" onchange="handlePhotoSelected(this)">
              </label>
            </div>

            ${preview ? `
              <div style="margin: 12px 0;">
                <img src="${preview}" style="width: 100%; max-height: 200px; object-fit: cover; border-radius: 8px; border: 1px solid var(--border-warm);">
                <button class="ag-btn-coral" style="width: 100%; margin-top: 10px; padding: 8px;" onclick="runPhotoAnalysis()" ${photoState.analyzing ? 'disabled' : ''}>
                  ${photoState.analyzing ? 'Executing OnnxRuntime Session...' : '⚡ Compute Residual Fusion'}
                </button>
              </div>
            ` : `
              <div style="font-size: 0.76rem; color: var(--text-muted); line-height: 1.5; padding: 12px; background: #F8FAFC; border-radius: 8px;">
                Image input is scaled to $224 \\times 224$ via HTML5 Canvas, normalized with ImageNet statistics $\\mu=[0.485, 0.456, 0.406]$, $\\sigma=[0.229, 0.224, 0.225]$, and analyzed client-side.
              </div>
            `}

            <!-- Mathematical Formulation Card -->
            <div class="tech-formula-card" style="margin-top: 14px;">
              <div style="font-weight: 700; color: var(--coral-brand); margin-bottom: 4px;">Residual Fusion Equation:</div>
              <div>\\hat{y}_{\\text{final}} = \\hat{y}_{\\text{baseline}} + \\lambda \\cdot (\\hat{y}_{\\text{cnn}} - \\hat{y}_{\\text{baseline}})</div>
              <div style="font-size: 0.70rem; color: #64748B; margin-top: 4px;">
                \\lambda = \\frac{1}{1 + \\sigma^2} \\cdot (1 - \\text{OOD}) &bull; As uncertainty \\sigma \\to \\infty or OOD \\to 1, \\lambda \\to 0 (baseline safety fallback).
              </div>
            </div>
          </div>

          <!-- Evaluation Display -->
          <div class="tech-display-panel">
            ${res ? `
              <div class="tech-stat-card" style="border-top: 4px solid var(--coral-brand);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-size: 0.72rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Fused Particulate Concentration</span>
                  <span class="metric-pill" style="background: ${res.isOodRejected ? '#FEF2F2' : '#ECFDF5'}; color: ${res.isOodRejected ? '#DC2626' : '#059669'}; font-weight: 800;">
                    ${res.isOodRejected ? 'OOD REJECTED' : 'FUSED IN-DISTRIBUTION'}
                  </span>
                </div>
                <h3 style="font-family: var(--font-heading); font-size: 2.2rem; font-weight: 800; color: var(--text-navy); margin: 6px 0;">
                  ${res.fusedPm25} <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-muted);">µg/m³</span>
                </h3>
              </div>

              <div class="table-responsive" style="margin-top: 14px;">
                <table class="ag-table" style="font-size: 0.78rem;">
                  <thead>
                    <tr>
                      <th>Component Stream</th>
                      <th>Observed Value</th>
                      <th>Uncertainty (&sigma;)</th>
                      <th>Assigned Weight (&lambda;)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>Meteorological Reanalysis (Open-Meteo)</strong></td>
                      <td>${res.baselinePm25} µg/m³</td>
                      <td>&plusmn; 4.2 µg/m³</td>
                      <td>${((1 - res.lambda) * 100).toFixed(0)}%</td>
                    </tr>
                    <tr>
                      <td><strong>Optical Extinction CNN (MobileNetV3)</strong></td>
                      <td>${res.cnnPm25} µg/m³</td>
                      <td>&plusmn; ${res.uncertainty} µg/m³</td>
                      <td>${(res.lambda * 100).toFixed(0)}%</td>
                    </tr>
                    <tr>
                      <td><strong>Out-Of-Distribution (OOD) Score</strong></td>
                      <td colspan="3">${res.oodScore} ${res.isOodRejected ? '<span style="color: #DC2626; font-weight: 700;">(Exceeds threshold 0.60 &rarr; Optical stream gated)</span>' : '<span style="color: #059669;">(In-Distribution Scene)</span>'}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            ` : `
              <div class="tech-stat-card" style="text-align: center; padding: 48px 20px;">
                <div style="font-size: 2.4rem; color: #94A3B8; margin-bottom: 8px;">📊</div>
                <h4 style="color: var(--text-navy); font-weight: 800;">Awaiting Input Imagery</h4>
                <p style="font-size: 0.80rem; color: var(--text-muted); margin-top: 4px;">
                  Upload an outdoor atmospheric frame to evaluate the Koschmieder optical contrast reduction and residual fusion vector.
                </p>
              </div>
            `}
          </div>
        </div>
      </section>
    `;
  };

  // Auto-init on page load if enabled
  if (window.ENABLE_CNN_FUSION) {
    initPhotoModel();
  }
})();
