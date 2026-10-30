/**
 * Verification Test: ENABLE_CNN_FUSION Feature Flag Behavior & Mode C Graceful Degradation
 * (tests/test_cnn_fusion_flag.js)
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log('=== Running AirFusion CNN Photo Module Flag Verification ===');

const htmlPath = path.join(__dirname, '..', 'public', 'index.html');
const jsPath = path.join(__dirname, '..', 'public', 'js', 'photo-aqi.js');

const htmlContent = fs.readFileSync(htmlPath, 'utf8');
const jsContent = fs.readFileSync(jsPath, 'utf8');

// Test 1: Flag defaults to false
assert(htmlContent.includes('window.ENABLE_CNN_FUSION = false;'), 'ENABLE_CNN_FUSION must default to false');
console.log('PASS: window.ENABLE_CNN_FUSION is defined and defaults to false.');

// Test 2: Externalized JS file inclusion
assert(htmlContent.includes('<script src="js/photo-aqi.js" defer></script>'), 'js/photo-aqi.js must be included via script tag');
console.log('PASS: photo-aqi.js is cleanly referenced without bloating index.html.');

// Test 3: Sidebar item exists and is hidden by default
assert(htmlContent.includes('id="nav-item-photo" style="display: none;"'), 'nav-item-photo must be hidden by default');
console.log('PASS: Sidebar photo navigation entry is hidden by default when flag is false.');

// Test 4: Route handling exists
assert(htmlContent.includes("case 'photo':"), "Route for 'photo' page must exist in renderCurrentPage()");
console.log("PASS: Route handler for 'photo' page exists.");

// Test 5: Verify Photo Module Mode C ("Model not trained yet") Logic in photo-aqi.js
assert(jsContent.includes('isModeC: true'), 'photoState must default to Mode C (isModeC: true)');
assert(jsContent.includes('MODEL CHECKPOINT PENDING TRAINING'), 'Mode C badge must be displayed when model is pending');
assert(jsContent.includes('TRAINING.md'), 'Mode C notice must cite TRAINING.md');
assert(jsContent.includes('Train_AirFusion_CNN.ipynb'), 'Mode C notice must cite Train_AirFusion_CNN.ipynb');
console.log('PASS: Mode C graceful degradation and training instructions are properly configured.');

// Test 6: Verify Residual Fusion formulation in photo-aqi.js
assert(jsContent.includes('computeResidualFusion'), 'computeResidualFusion function must exist');
assert(jsContent.includes('final = baseline + lambda * (cnn - baseline)'), 'Residual fusion equation must be documented in header');
console.log('PASS: Residual fusion formulation is mathematically defined.');

// Test 7: Verify Open Datasets citations in Data & Credits
const openDatasets = [
  'PM25Vision',
  'DeadCardassian/PM25Vision',
  'CC-BY-4.0',
  'Air Pollution Image Dataset from India',
  'CC0-1.0',
  'Dhaka Smartphone PM2.5 Dataset',
  'HVAQ'
];

openDatasets.forEach(ds => {
  assert(jsContent.includes(ds), `Data & Credits must cite ${ds}`);
});
console.log('PASS: All 4 open datasets with licenses are cited in Data & Credits section.');

// Test 8: Verify simulation of flag = true
const mockWindow = {
  ENABLE_CNN_FUSION: true,
  state: {
    telemetry: {
      pm25: 42.5,
      city: 'Delhi',
      aqi: 118
    }
  }
};

// Evaluate photo-aqi.js inside mock sandbox
const vm = require('vm');
const context = vm.createContext({
  window: mockWindow,
  document: {
    createElement: () => ({ getContext: () => ({ drawImage: () => {}, getImageData: () => ({ data: new Uint8Array(224 * 224 * 4) }) }) }),
    head: { appendChild: () => {} }
  },
  console: console,
  FileReader: function() {},
  Image: function() {}
});

vm.runInContext(jsContent, context);

assert(typeof mockWindow.renderPhotoAqiSimple === 'function', 'renderPhotoAqiSimple must be exported to window');
assert(typeof mockWindow.renderPhotoAqiTechnical === 'function', 'renderPhotoAqiTechnical must be exported to window');

const simpleHtml = mockWindow.renderPhotoAqiSimple();
const techHtml = mockWindow.renderPhotoAqiTechnical();

assert(simpleHtml.includes('MODEL CHECKPOINT PENDING TRAINING (MODE C)'), 'Mode C notice must render in Simple mode');
assert(techHtml.includes('MODE C &bull; STRUCTURAL BASELINE ONLY'), 'Mode C notice must render in Technical mode');
assert(techHtml.includes('Residual Fusion Equation:'), 'Formula must render in Technical mode');

console.log('PASS: Mock evaluation with ENABLE_CNN_FUSION=true renders Mode C successfully in both Simple and Technical modes.');

console.log('\n=== All 8 Phase 2 CNN Module Tests Passed! ===\n');
