"""
Pytest Unit Test Suite for Golden Atmospheric Physics Vectors.
Verifies analytical calculations against shared cross-language test vectors in tests/golden/*.json.
"""

import sys
import json
from pathlib import Path
import pytest

# Ensure airfusion root is in sys.path
AIRFUSION_DIR = Path(__file__).resolve().parent.parent
if str(AIRFUSION_DIR) not in sys.path:
    sys.path.insert(0, str(AIRFUSION_DIR))

from src.physics_models import (
    calc_gaussian_sigmas,
    calc_ground_concentration,
    calc_koehler_growth,
    calc_koehler_corrected,
    calc_angstrom_exponent,
    calc_extrapolated_aod,
    calc_ventilation_coefficient,
    calc_aqi_subindex
)

GOLDEN_DIR = AIRFUSION_DIR.parent / "tests" / "golden"


def test_golden_gaussian_plume():
    path = GOLDEN_DIR / "gaussian_plume.json"
    assert path.exists(), f"Missing golden vector file {path}"
    with open(path, "r", encoding="utf-8") as f:
        vectors = json.load(f)

    for v in vectors:
        sy, sz = calc_gaussian_sigmas(v["stability_class"], v["downwind_dist_m"])
        conc = calc_ground_concentration(
            v["emission_rate_gs"],
            v["stack_height_m"],
            v["wind_speed_ms"],
            v["stability_class"],
            v["downwind_dist_m"],
            v["crosswind_dist_m"]
        )
        assert abs(sy - v["sigma_y_m"]) < 1e-3
        assert abs(sz - v["sigma_z_m"]) < 1e-3
        assert abs(conc - v["expected_concentration_ug_m3"]) < 1e-2


def test_golden_koehler_growth():
    path = GOLDEN_DIR / "koehler_growth.json"
    assert path.exists(), f"Missing golden vector file {path}"
    with open(path, "r", encoding="utf-8") as f:
        vectors = json.load(f)

    for v in vectors:
        f_rh = calc_koehler_growth(v["relative_humidity"], v["a_coeff"], v["b_coeff"])
        corrected = calc_koehler_corrected(
            v["raw_pm25"],
            v["zero_offset"],
            v["span_coeff"],
            v["relative_humidity"],
            v["a_coeff"],
            v["b_coeff"]
        )
        assert abs(f_rh - v["expected_f_rh"]) < 1e-3
        assert abs(corrected - v["expected_corrected_pm25"]) < 1e-2


def test_golden_angstrom_aod():
    path = GOLDEN_DIR / "angstrom_aod.json"
    assert path.exists(), f"Missing golden vector file {path}"
    with open(path, "r", encoding="utf-8") as f:
        vectors = json.load(f)

    for v in vectors:
        alpha = calc_angstrom_exponent(v["tau_440"], v["tau_870"])
        tau550 = calc_extrapolated_aod(v["tau_440"], alpha, 550.0, 440.0)
        assert abs(alpha - v["expected_alpha"]) < 1e-3
        assert abs(tau550 - v["expected_tau_550"]) < 1e-3


def test_golden_ventilation_coefficient():
    path = GOLDEN_DIR / "ventilation_coefficient.json"
    assert path.exists(), f"Missing golden vector file {path}"
    with open(path, "r", encoding="utf-8") as f:
        vectors = json.load(f)

    for v in vectors:
        vi = calc_ventilation_coefficient(v["pbl_height_m"], v["wind_speed_kmh"])
        assert abs(vi - v["expected_ventilation_index_m2_s"]) <= 1.0


def test_golden_aqi_subindices():
    path = GOLDEN_DIR / "aqi_subindices.json"
    assert path.exists(), f"Missing golden vector file {path}"
    with open(path, "r", encoding="utf-8") as f:
        vectors = json.load(f)

    for v in vectors:
        res = calc_aqi_subindex(v["pollutant"], v["concentration"], v["standard"])
        assert res["aqi"] == v["expected_aqi"]
        assert res["category"] == v["expected_category"]
