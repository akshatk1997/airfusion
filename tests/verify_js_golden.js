/**
 * Node.js Verification Test Runner for AirFusion Shared Golden Test Vectors.
 * Validates that client-side JavaScript atmospheric physics matches Python exactly.
 */

const fs = require('fs');
const path = require('path');

const GOLDEN_DIR = path.join(__dirname, 'golden');

// 1. Briggs Gaussian Dispersion Sigmas
function calcGaussianSigmas(st, x) {
  const x_val = Math.max(10.0, parseFloat(x));
  let sy = 0, sz = 0;
  switch (st.toUpperCase()) {
    case 'A':
      sy = 0.22 * x_val * Math.pow(1.0 + 0.0001 * x_val, -0.5);
      sz = 0.20 * x_val;
      break;
    case 'B':
      sy = 0.16 * x_val * Math.pow(1.0 + 0.0001 * x_val, -0.5);
      sz = 0.12 * x_val;
      break;
    case 'C':
      sy = 0.11 * x_val * Math.pow(1.0 + 0.0001 * x_val, -0.5);
      sz = 0.08 * x_val * Math.pow(1.0 + 0.0002 * x_val, -0.5);
      break;
    case 'D':
      sy = 0.08 * x_val * Math.pow(1.0 + 0.0001 * x_val, -0.5);
      sz = 0.06 * x_val * Math.pow(1.0 + 0.0015 * x_val, -0.5);
      break;
    case 'E':
      sy = 0.06 * x_val * Math.pow(1.0 + 0.0001 * x_val, -0.5);
      sz = 0.03 * x_val * Math.pow(1.0 + 0.0003 * x_val, -1.0);
      break;
    case 'F':
    default:
      sy = 0.04 * x_val * Math.pow(1.0 + 0.0001 * x_val, -0.5);
      sz = 0.016 * x_val * Math.pow(1.0 + 0.0003 * x_val, -1.0);
      break;
  }
  return { sy: Math.max(0.1, sy), sz: Math.max(0.1, sz) };
}

function calcGroundConcentration(q, h, u, st, x, y) {
  const { sy, sz } = calcGaussianSigmas(st, x);
  const u_safe = Math.max(0.5, parseFloat(u));
  const expY = Math.exp(-Math.min(50.0, (y * y) / (2.0 * sy * sy)));
  const expZ = Math.exp(-Math.min(50.0, (h * h) / (2.0 * sz * sz)));
  const conc = (q / (Math.PI * u_safe * sy * sz)) * expY * expZ * 1e6;
  return conc;
}

// 2. Koehler Growth & Sensor Correction
function calcKoehlerGrowth(rh, a = 0.25, b = 0.90) {
  const safeRH = Math.min(98.5, Math.max(0.0, parseFloat(rh)));
  return 1.0 + a * Math.pow(safeRH / (100.0 - safeRH), b);
}

function calcKoehlerCorrected(raw, zero = 0.0, span = 1.0, rh = 50.0, a = 0.25, b = 0.90) {
  const fRH = calcKoehlerGrowth(rh, a, b);
  const safeSpan = Math.max(0.01, parseFloat(span));
  return Math.max(0.1, (parseFloat(raw) - parseFloat(zero)) / (safeSpan * fRH));
}

// 3. Angstrom Turbidity Exponent & Extrapolated AOD
function calcAngstromExponent(tau440, tau870) {
  const t1 = Math.max(0.001, parseFloat(tau440));
  const t2 = Math.max(0.001, parseFloat(tau870));
  const alpha = (Math.log(t1) - Math.log(t2)) / 0.681739;
  return Math.max(-0.5, Math.min(3.0, alpha));
}

function calcExtrapolatedAod(tau440, alpha, targetWl = 550.0, baseWl = 440.0) {
  const ratio = targetWl / baseWl;
  return Math.max(0.01, parseFloat(tau440) * Math.pow(ratio, -alpha));
}

// 4. Boundary Layer Ventilation Index
function calcVentilationIndex(pblHeight, windKmh) {
  return Math.round(parseFloat(pblHeight) * (parseFloat(windKmh) / 3.6));
}

// 5. AQI Breakpoint Tables
const EPA_BREAKPOINTS = {
  pm25: [
    { cLo: 0.0, cHi: 12.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 12.1, cHi: 35.4, iLo: 51, iHi: 100, cat: 'Moderate' },
    { cLo: 35.5, cHi: 55.4, iLo: 101, iHi: 150, cat: 'Unhealthy for Sensitive Groups' },
    { cLo: 55.5, cHi: 150.4, iLo: 151, iHi: 200, cat: 'Unhealthy' },
    { cLo: 150.5, cHi: 250.4, iLo: 201, iHi: 300, cat: 'Very Unhealthy' },
    { cLo: 250.5, cHi: 350.4, iLo: 301, iHi: 400, cat: 'Hazardous' },
    { cLo: 350.5, cHi: 500.4, iLo: 401, iHi: 500, cat: 'Hazardous' }
  ],
  pm10: [
    { cLo: 0.0, cHi: 54.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 55.0, cHi: 154.0, iLo: 51, iHi: 100, cat: 'Moderate' },
    { cLo: 155.0, cHi: 254.0, iLo: 101, iHi: 150, cat: 'Unhealthy for Sensitive Groups' },
    { cLo: 255.0, cHi: 354.0, iLo: 151, iHi: 200, cat: 'Unhealthy' },
    { cLo: 355.0, cHi: 424.0, iLo: 201, iHi: 300, cat: 'Very Unhealthy' },
    { cLo: 425.0, cHi: 504.0, iLo: 301, iHi: 400, cat: 'Hazardous' },
    { cLo: 505.0, cHi: 604.0, iLo: 401, iHi: 500, cat: 'Hazardous' }
  ],
  no2: [
    { cLo: 0.0, cHi: 53.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 54.0, cHi: 100.0, iLo: 51, iHi: 100, cat: 'Moderate' },
    { cLo: 101.0, cHi: 360.0, iLo: 101, iHi: 150, cat: 'Unhealthy for Sensitive Groups' },
    { cLo: 361.0, cHi: 649.0, iLo: 151, iHi: 200, cat: 'Unhealthy' },
    { cLo: 650.0, cHi: 1249.0, iLo: 201, iHi: 300, cat: 'Very Unhealthy' },
    { cLo: 1250.0, cHi: 1649.0, iLo: 301, iHi: 400, cat: 'Hazardous' },
    { cLo: 1650.0, cHi: 2049.0, iLo: 401, iHi: 500, cat: 'Hazardous' }
  ],
  so2: [
    { cLo: 0.0, cHi: 35.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 36.0, cHi: 75.0, iLo: 51, iHi: 100, cat: 'Moderate' },
    { cLo: 76.0, cHi: 185.0, iLo: 101, iHi: 150, cat: 'Unhealthy for Sensitive Groups' },
    { cLo: 186.0, cHi: 304.0, iLo: 151, iHi: 200, cat: 'Unhealthy' },
    { cLo: 305.0, cHi: 604.0, iLo: 201, iHi: 300, cat: 'Very Unhealthy' },
    { cLo: 605.0, cHi: 804.0, iLo: 301, iHi: 400, cat: 'Hazardous' },
    { cLo: 805.0, cHi: 1004.0, iLo: 401, iHi: 500, cat: 'Hazardous' }
  ],
  co: [
    { cLo: 0.0, cHi: 4.4, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 4.5, cHi: 9.4, iLo: 51, iHi: 100, cat: 'Moderate' },
    { cLo: 9.5, cHi: 12.4, iLo: 101, iHi: 150, cat: 'Unhealthy for Sensitive Groups' },
    { cLo: 12.5, cHi: 15.4, iLo: 151, iHi: 200, cat: 'Unhealthy' },
    { cLo: 15.5, cHi: 30.4, iLo: 201, iHi: 300, cat: 'Very Unhealthy' },
    { cLo: 30.5, cHi: 40.4, iLo: 301, iHi: 400, cat: 'Hazardous' },
    { cLo: 40.5, cHi: 50.4, iLo: 401, iHi: 500, cat: 'Hazardous' }
  ],
  o3: [
    { cLo: 0.0, cHi: 54.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 55.0, cHi: 70.0, iLo: 51, iHi: 100, cat: 'Moderate' },
    { cLo: 71.0, cHi: 85.0, iLo: 101, iHi: 150, cat: 'Unhealthy for Sensitive Groups' },
    { cLo: 86.0, cHi: 105.0, iLo: 151, iHi: 200, cat: 'Unhealthy' },
    { cLo: 106.0, cHi: 200.0, iLo: 201, iHi: 300, cat: 'Very Unhealthy' },
    { cLo: 201.0, cHi: 404.0, iLo: 301, iHi: 400, cat: 'Hazardous' },
    { cLo: 405.0, cHi: 504.0, iLo: 401, iHi: 500, cat: 'Hazardous' }
  ]
};

const CPCB_BREAKPOINTS = {
  pm25: [
    { cLo: 0.0, cHi: 30.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 31.0, cHi: 60.0, iLo: 51, iHi: 100, cat: 'Satisfactory' },
    { cLo: 61.0, cHi: 90.0, iLo: 101, iHi: 200, cat: 'Moderate' },
    { cLo: 91.0, cHi: 120.0, iLo: 201, iHi: 300, cat: 'Poor' },
    { cLo: 121.0, cHi: 250.0, iLo: 301, iHi: 400, cat: 'Very Poor' },
    { cLo: 251.0, cHi: 500.0, iLo: 401, iHi: 500, cat: 'Severe' }
  ],
  pm10: [
    { cLo: 0.0, cHi: 50.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 51.0, cHi: 100.0, iLo: 51, iHi: 100, cat: 'Satisfactory' },
    { cLo: 101.0, cHi: 250.0, iLo: 101, iHi: 200, cat: 'Moderate' },
    { cLo: 251.0, cHi: 350.0, iLo: 201, iHi: 300, cat: 'Poor' },
    { cLo: 351.0, cHi: 430.0, iLo: 301, iHi: 400, cat: 'Very Poor' },
    { cLo: 431.0, cHi: 600.0, iLo: 401, iHi: 500, cat: 'Severe' }
  ],
  no2: [
    { cLo: 0.0, cHi: 40.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 41.0, cHi: 80.0, iLo: 51, iHi: 100, cat: 'Satisfactory' },
    { cLo: 81.0, cHi: 180.0, iLo: 101, iHi: 200, cat: 'Moderate' },
    { cLo: 181.0, cHi: 280.0, iLo: 201, iHi: 300, cat: 'Poor' },
    { cLo: 281.0, cHi: 400.0, iLo: 301, iHi: 400, cat: 'Very Poor' },
    { cLo: 401.0, cHi: 600.0, iLo: 401, iHi: 500, cat: 'Severe' }
  ],
  so2: [
    { cLo: 0.0, cHi: 40.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 41.0, cHi: 80.0, iLo: 51, iHi: 100, cat: 'Satisfactory' },
    { cLo: 81.0, cHi: 380.0, iLo: 101, iHi: 200, cat: 'Moderate' },
    { cLo: 381.0, cHi: 800.0, iLo: 201, iHi: 300, cat: 'Poor' },
    { cLo: 801.0, cHi: 1600.0, iLo: 301, iHi: 400, cat: 'Very Poor' },
    { cLo: 1601.0, cHi: 2000.0, iLo: 401, iHi: 500, cat: 'Severe' }
  ],
  co: [
    { cLo: 0.0, cHi: 1.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 1.1, cHi: 2.0, iLo: 51, iHi: 100, cat: 'Satisfactory' },
    { cLo: 2.1, cHi: 10.0, iLo: 101, iHi: 200, cat: 'Moderate' },
    { cLo: 10.1, cHi: 17.0, iLo: 201, iHi: 300, cat: 'Poor' },
    { cLo: 17.1, cHi: 34.0, iLo: 301, iHi: 400, cat: 'Very Poor' },
    { cLo: 34.1, cHi: 50.0, iLo: 401, iHi: 500, cat: 'Severe' }
  ],
  o3: [
    { cLo: 0.0, cHi: 50.0, iLo: 0, iHi: 50, cat: 'Good' },
    { cLo: 51.0, cHi: 100.0, iLo: 51, iHi: 100, cat: 'Satisfactory' },
    { cLo: 101.0, cHi: 168.0, iLo: 101, iHi: 200, cat: 'Moderate' },
    { cLo: 169.0, cHi: 208.0, iLo: 201, iHi: 300, cat: 'Poor' },
    { cLo: 209.0, cHi: 748.0, iLo: 301, iHi: 400, cat: 'Very Poor' },
    { cLo: 749.0, cHi: 1000.0, iLo: 401, iHi: 500, cat: 'Severe' }
  ]
};

function calcAqiSubindex(pollutant, conc, standard = 'EPA') {
  const pKey = pollutant.toLowerCase().replace(/[\._]/g, '');
  const key = (pKey === 'pm25' || pKey === 'pm2_5') ? 'pm25' : (pKey === 'pm10' ? 'pm10' : pKey);
  const table = (standard.toUpperCase() === 'CPCB') ? CPCB_BREAKPOINTS : EPA_BREAKPOINTS;
  const bps = table[key] || table.pm25;
  const c = Math.max(0.0, parseFloat(conc));

  for (let i = 0; i < bps.length; i++) {
    const bp = bps[i];
    if (c >= bp.cLo && c <= bp.cHi) {
      const aqi = Math.round(((bp.iHi - bp.iLo) / (bp.cHi - bp.cLo)) * (c - bp.cLo) + bp.iLo);
      return { aqi: Math.min(500, Math.max(0, aqi)), category: bp.cat };
    }
  }
  const last = bps[bps.length - 1];
  return { aqi: 500, category: last.cat };
}

// ==============================================================================
// TEST EXECUTION
// ==============================================================================

function runTests() {
  console.log("=== Running Node.js Golden Vector Physics Verifications ===");
  let passed = 0;
  let failed = 0;

  function assert(condition, message) {
    if (!condition) {
      console.error(`FAIL: ${message}`);
      failed++;
    } else {
      passed++;
    }
  }

  // 1. Gaussian Plume
  const plumeVectors = JSON.parse(fs.readFileSync(path.join(GOLDEN_DIR, 'gaussian_plume.json'), 'utf-8'));
  for (const v of plumeVectors) {
    const { sy, sz } = calcGaussianSigmas(v.stability_class, v.downwind_dist_m);
    const conc = calcGroundConcentration(
      v.emission_rate_gs,
      v.stack_height_m,
      v.wind_speed_ms,
      v.stability_class,
      v.downwind_dist_m,
      v.crosswind_dist_m
    );
    assert(Math.abs(sy - v.sigma_y_m) < 1e-3, `Gaussian sy mismatch for x=${v.downwind_dist_m}`);
    assert(Math.abs(sz - v.sigma_z_m) < 1e-3, `Gaussian sz mismatch for x=${v.downwind_dist_m}`);
    assert(Math.abs(conc - v.expected_concentration_ug_m3) < 1e-2, `Gaussian conc mismatch for ${JSON.stringify(v)}`);
  }

  // 2. Koehler Growth
  const koehlerVectors = JSON.parse(fs.readFileSync(path.join(GOLDEN_DIR, 'koehler_growth.json'), 'utf-8'));
  for (const v of koehlerVectors) {
    const fRH = calcKoehlerGrowth(v.relative_humidity, v.a_coeff, v.b_coeff);
    const corrected = calcKoehlerCorrected(v.raw_pm25, v.zero_offset, v.span_coeff, v.relative_humidity, v.a_coeff, v.b_coeff);
    assert(Math.abs(fRH - v.expected_f_rh) < 1e-3, `Koehler f(RH) mismatch for RH=${v.relative_humidity}`);
    assert(Math.abs(corrected - v.expected_corrected_pm25) < 1e-2, `Koehler corrected mismatch`);
  }

  // 3. Angstrom AOD
  const angstromVectors = JSON.parse(fs.readFileSync(path.join(GOLDEN_DIR, 'angstrom_aod.json'), 'utf-8'));
  for (const v of angstromVectors) {
    const alpha = calcAngstromExponent(v.tau_440, v.tau_870);
    const tau550 = calcExtrapolatedAod(v.tau_440, alpha, 550.0, 440.0);
    assert(Math.abs(alpha - v.expected_alpha) < 1e-3, `Angstrom alpha mismatch for tau440=${v.tau_440}`);
    assert(Math.abs(tau550 - v.expected_tau_550) < 1e-3, `Angstrom tau550 mismatch`);
  }

  // 4. Ventilation Coefficient
  const ventVectors = JSON.parse(fs.readFileSync(path.join(GOLDEN_DIR, 'ventilation_coefficient.json'), 'utf-8'));
  for (const v of ventVectors) {
    const vi = calcVentilationIndex(v.pbl_height_m, v.wind_speed_kmh);
    assert(Math.abs(vi - v.expected_ventilation_index_m2_s) <= 1, `Ventilation mismatch`);
  }

  // 5. AQI Sub-Indices
  const aqiVectors = JSON.parse(fs.readFileSync(path.join(GOLDEN_DIR, 'aqi_subindices.json'), 'utf-8'));
  for (const v of aqiVectors) {
    const res = calcAqiSubindex(v.pollutant, v.concentration, v.standard);
    assert(res.aqi === v.expected_aqi, `AQI mismatch for ${v.pollutant} ${v.concentration} ${v.standard}: got ${res.aqi}, expected ${v.expected_aqi}`);
    assert(res.category === v.expected_category, `Category mismatch for ${v.pollutant} ${v.concentration} ${v.standard}`);
  }

  console.log(`Node.js Verifications Complete: ${passed} assertions passed, ${failed} failed.`);
  if (failed > 0) {
    process.exit(1);
  }
}

runTests();
