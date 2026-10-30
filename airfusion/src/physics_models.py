"""
Standardized Physical & Metrological Atmospheric Models for AirFusion.
Provides analytical formulas matching client-side JavaScript implementations:
1. Gaussian Plume Dispersion (Briggs / Pasquill-Gifford parameters)
2. Köhler Hygroscopic Growth Correction (f(RH))
3. Ångström Turbidity Exponent & Multi-wavelength AOD Extrapolation
4. Planetary Boundary Layer Ventilation Index
5. Multi-Pollutant AQI Sub-Index Calculation (US EPA & CPCB Official Breakpoints)
"""

from __future__ import annotations
import math
from typing import Dict, Any, Tuple, Optional


def calc_gaussian_sigmas(stability: str, x: float) -> Tuple[float, float]:
    """
    Computes Briggs horizontal (sigma_y) and vertical (sigma_z) dispersion parameters (in meters).
    x: downwind distance in meters.
    stability: Pasquill-Gifford atmospheric stability class ('A', 'B', 'C', 'D', 'E', 'F').
    """
    x_val = max(10.0, float(x))
    st = stability.upper()

    if st == 'A':
        sy = 0.22 * x_val * math.pow(1.0 + 0.0001 * x_val, -0.5)
        sz = 0.20 * x_val
    elif st == 'B':
        sy = 0.16 * x_val * math.pow(1.0 + 0.0001 * x_val, -0.5)
        sz = 0.12 * x_val
    elif st == 'C':
        sy = 0.11 * x_val * math.pow(1.0 + 0.0001 * x_val, -0.5)
        sz = 0.08 * x_val * math.pow(1.0 + 0.0002 * x_val, -0.5)
    elif st == 'D':
        sy = 0.08 * x_val * math.pow(1.0 + 0.0001 * x_val, -0.5)
        sz = 0.06 * x_val * math.pow(1.0 + 0.0015 * x_val, -0.5)
    elif st == 'E':
        sy = 0.06 * x_val * math.pow(1.0 + 0.0001 * x_val, -0.5)
        sz = 0.03 * x_val * math.pow(1.0 + 0.0003 * x_val, -1.0)
    else:  # 'F'
        sy = 0.04 * x_val * math.pow(1.0 + 0.0001 * x_val, -0.5)
        sz = 0.016 * x_val * math.pow(1.0 + 0.0003 * x_val, -1.0)

    return max(0.1, sy), max(0.1, sz)


def calc_ground_concentration(
    q: float,
    h: float,
    u: float,
    stability: str,
    x: float,
    y: float
) -> float:
    """
    Calculates steady-state ground-level particulate concentration C(x, y, 0) in ug/m3.
    q: emission rate (g/s)
    h: effective stack height (m)
    u: wind speed at release height (m/s)
    stability: stability class ('A' to 'F')
    x: downwind distance (m)
    y: crosswind distance (m)
    """
    sy, sz = calc_gaussian_sigmas(stability, x)
    u_safe = max(0.5, float(u))
    exp_y = math.exp(-min(50.0, (y * y) / (2.0 * sy * sy)))
    exp_z = math.exp(-min(50.0, (h * h) / (2.0 * sz * sz)))
    # Ground-level concentration with 2x surface reflection:
    c_g = (q / (math.pi * u_safe * sy * sz)) * exp_y * exp_z
    return float(c_g * 1e6)  # convert g/m3 to ug/m3


def calc_koehler_growth(rh: float, a: float = 0.25, b: float = 0.90) -> float:
    """
    Calculates empirical hygroscopic growth factor f(RH) for aerosol particulates.
    rh: relative humidity percentage (0-100)
    a, b: fitting coefficients
    """
    safe_rh = min(98.5, max(0.0, float(rh)))
    ratio = safe_rh / (100.0 - safe_rh)
    return float(1.0 + a * math.pow(ratio, b))


def calc_koehler_corrected(
    raw: float,
    zero: float = 0.0,
    span: float = 1.0,
    rh: float = 50.0,
    a: float = 0.25,
    b: float = 0.90
) -> float:
    """
    Removes hygroscopic water mass artifact and sensor calibration offsets.
    """
    f_rh = calc_koehler_growth(rh, a, b)
    safe_span = max(0.01, float(span))
    corrected = (float(raw) - float(zero)) / (safe_span * f_rh)
    return max(0.1, float(corrected))


def calc_angstrom_exponent(tau440: float, tau870: float) -> float:
    """
    Calculates Ångström turbidity parameter alpha between 440nm and 870nm:
    alpha = - ln(tau440 / tau870) / ln(440 / 870)
    ln(870/440) = 0.681739
    """
    t1 = max(0.001, float(tau440))
    t2 = max(0.001, float(tau870))
    alpha = (math.log(t1) - math.log(t2)) / 0.681739
    return float(max(-0.5, min(3.0, alpha)))


def calc_extrapolated_aod(
    tau440: float,
    alpha: float,
    target_wavelength: float = 550.0,
    base_wavelength: float = 440.0
) -> float:
    """
    Extrapolates aerosol optical depth to target wavelength:
    tau(lambda) = tau(lambda_0) * (lambda / lambda_0)^(-alpha)
    """
    ratio = target_wavelength / base_wavelength
    return float(max(0.01, float(tau440) * math.pow(ratio, -float(alpha))))


def calc_ventilation_coefficient(pbl_height: float, wind_kmh: float) -> float:
    """
    Calculates planetary boundary layer ventilation coefficient V_c in m^2/s:
    V_c = PBLH * U_10 (where U_10 is in m/s)
    """
    wind_ms = float(wind_kmh) / 3.6
    return float(round(float(pbl_height) * wind_ms))


# ==============================================================================
# OFFICIAL AQI BREAKPOINT TABLES (US EPA & INDIAN CPCB)
# ==============================================================================

EPA_BREAKPOINTS = {
    'pm25': [
        {'cLo': 0.0, 'cHi': 12.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 12.1, 'cHi': 35.4, 'iLo': 51, 'iHi': 100, 'cat': 'Moderate'},
        {'cLo': 35.5, 'cHi': 55.4, 'iLo': 101, 'iHi': 150, 'cat': 'Unhealthy for Sensitive Groups'},
        {'cLo': 55.5, 'cHi': 150.4, 'iLo': 151, 'iHi': 200, 'cat': 'Unhealthy'},
        {'cLo': 150.5, 'cHi': 250.4, 'iLo': 201, 'iHi': 300, 'cat': 'Very Unhealthy'},
        {'cLo': 250.5, 'cHi': 350.4, 'iLo': 301, 'iHi': 400, 'cat': 'Hazardous'},
        {'cLo': 350.5, 'cHi': 500.4, 'iLo': 401, 'iHi': 500, 'cat': 'Hazardous'}
    ],
    'pm10': [
        {'cLo': 0.0, 'cHi': 54.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 55.0, 'cHi': 154.0, 'iLo': 51, 'iHi': 100, 'cat': 'Moderate'},
        {'cLo': 155.0, 'cHi': 254.0, 'iLo': 101, 'iHi': 150, 'cat': 'Unhealthy for Sensitive Groups'},
        {'cLo': 255.0, 'cHi': 354.0, 'iLo': 151, 'iHi': 200, 'cat': 'Unhealthy'},
        {'cLo': 355.0, 'cHi': 424.0, 'iLo': 201, 'iHi': 300, 'cat': 'Very Unhealthy'},
        {'cLo': 425.0, 'cHi': 504.0, 'iLo': 301, 'iHi': 400, 'cat': 'Hazardous'},
        {'cLo': 505.0, 'cHi': 604.0, 'iLo': 401, 'iHi': 500, 'cat': 'Hazardous'}
    ],
    'no2': [
        {'cLo': 0.0, 'cHi': 53.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 54.0, 'cHi': 100.0, 'iLo': 51, 'iHi': 100, 'cat': 'Moderate'},
        {'cLo': 101.0, 'cHi': 360.0, 'iLo': 101, 'iHi': 150, 'cat': 'Unhealthy for Sensitive Groups'},
        {'cLo': 361.0, 'cHi': 649.0, 'iLo': 151, 'iHi': 200, 'cat': 'Unhealthy'},
        {'cLo': 650.0, 'cHi': 1249.0, 'iLo': 201, 'iHi': 300, 'cat': 'Very Unhealthy'},
        {'cLo': 1250.0, 'cHi': 1649.0, 'iLo': 301, 'iHi': 400, 'cat': 'Hazardous'},
        {'cLo': 1650.0, 'cHi': 2049.0, 'iLo': 401, 'iHi': 500, 'cat': 'Hazardous'}
    ],
    'so2': [
        {'cLo': 0.0, 'cHi': 35.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 36.0, 'cHi': 75.0, 'iLo': 51, 'iHi': 100, 'cat': 'Moderate'},
        {'cLo': 76.0, 'cHi': 185.0, 'iLo': 101, 'iHi': 150, 'cat': 'Unhealthy for Sensitive Groups'},
        {'cLo': 186.0, 'cHi': 304.0, 'iLo': 151, 'iHi': 200, 'cat': 'Unhealthy'},
        {'cLo': 305.0, 'cHi': 604.0, 'iLo': 201, 'iHi': 300, 'cat': 'Very Unhealthy'},
        {'cLo': 605.0, 'cHi': 804.0, 'iLo': 301, 'iHi': 400, 'cat': 'Hazardous'},
        {'cLo': 805.0, 'cHi': 1004.0, 'iLo': 401, 'iHi': 500, 'cat': 'Hazardous'}
    ],
    'co': [
        # EPA CO is in ppm (1 mg/m3 approx 0.873 ppm)
        {'cLo': 0.0, 'cHi': 4.4, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 4.5, 'cHi': 9.4, 'iLo': 51, 'iHi': 100, 'cat': 'Moderate'},
        {'cLo': 9.5, 'cHi': 12.4, 'iLo': 101, 'iHi': 150, 'cat': 'Unhealthy for Sensitive Groups'},
        {'cLo': 12.5, 'cHi': 15.4, 'iLo': 151, 'iHi': 200, 'cat': 'Unhealthy'},
        {'cLo': 15.5, 'cHi': 30.4, 'iLo': 201, 'iHi': 300, 'cat': 'Very Unhealthy'},
        {'cLo': 30.5, 'cHi': 40.4, 'iLo': 301, 'iHi': 400, 'cat': 'Hazardous'},
        {'cLo': 40.5, 'cHi': 50.4, 'iLo': 401, 'iHi': 500, 'cat': 'Hazardous'}
    ],
    'o3': [
        {'cLo': 0.0, 'cHi': 54.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 55.0, 'cHi': 70.0, 'iLo': 51, 'iHi': 100, 'cat': 'Moderate'},
        {'cLo': 71.0, 'cHi': 85.0, 'iLo': 101, 'iHi': 150, 'cat': 'Unhealthy for Sensitive Groups'},
        {'cLo': 86.0, 'cHi': 105.0, 'iLo': 151, 'iHi': 200, 'cat': 'Unhealthy'},
        {'cLo': 106.0, 'cHi': 200.0, 'iLo': 201, 'iHi': 300, 'cat': 'Very Unhealthy'},
        {'cLo': 201.0, 'cHi': 404.0, 'iLo': 301, 'iHi': 400, 'cat': 'Hazardous'},
        {'cLo': 405.0, 'cHi': 504.0, 'iLo': 401, 'iHi': 500, 'cat': 'Hazardous'}
    ]
}

# Central Pollution Control Board (India) National Air Quality Index Standard
CPCB_BREAKPOINTS = {
    'pm25': [
        {'cLo': 0.0, 'cHi': 30.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 31.0, 'cHi': 60.0, 'iLo': 51, 'iHi': 100, 'cat': 'Satisfactory'},
        {'cLo': 61.0, 'cHi': 90.0, 'iLo': 101, 'iHi': 200, 'cat': 'Moderate'},
        {'cLo': 91.0, 'cHi': 120.0, 'iLo': 201, 'iHi': 300, 'cat': 'Poor'},
        {'cLo': 121.0, 'cHi': 250.0, 'iLo': 301, 'iHi': 400, 'cat': 'Very Poor'},
        {'cLo': 251.0, 'cHi': 500.0, 'iLo': 401, 'iHi': 500, 'cat': 'Severe'}
    ],
    'pm10': [
        {'cLo': 0.0, 'cHi': 50.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 51.0, 'cHi': 100.0, 'iLo': 51, 'iHi': 100, 'cat': 'Satisfactory'},
        {'cLo': 101.0, 'cHi': 250.0, 'iLo': 101, 'iHi': 200, 'cat': 'Moderate'},
        {'cLo': 251.0, 'cHi': 350.0, 'iLo': 201, 'iHi': 300, 'cat': 'Poor'},
        {'cLo': 351.0, 'cHi': 430.0, 'iLo': 301, 'iHi': 400, 'cat': 'Very Poor'},
        {'cLo': 431.0, 'cHi': 600.0, 'iLo': 401, 'iHi': 500, 'cat': 'Severe'}
    ],
    'no2': [
        {'cLo': 0.0, 'cHi': 40.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 41.0, 'cHi': 80.0, 'iLo': 51, 'iHi': 100, 'cat': 'Satisfactory'},
        {'cLo': 81.0, 'cHi': 180.0, 'iLo': 101, 'iHi': 200, 'cat': 'Moderate'},
        {'cLo': 181.0, 'cHi': 280.0, 'iLo': 201, 'iHi': 300, 'cat': 'Poor'},
        {'cLo': 281.0, 'cHi': 400.0, 'iLo': 301, 'iHi': 400, 'cat': 'Very Poor'},
        {'cLo': 401.0, 'cHi': 600.0, 'iLo': 401, 'iHi': 500, 'cat': 'Severe'}
    ],
    'so2': [
        {'cLo': 0.0, 'cHi': 40.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 41.0, 'cHi': 80.0, 'iLo': 51, 'iHi': 100, 'cat': 'Satisfactory'},
        {'cLo': 81.0, 'cHi': 380.0, 'iLo': 101, 'iHi': 200, 'cat': 'Moderate'},
        {'cLo': 381.0, 'cHi': 800.0, 'iLo': 201, 'iHi': 300, 'cat': 'Poor'},
        {'cLo': 801.0, 'cHi': 1600.0, 'iLo': 301, 'iHi': 400, 'cat': 'Very Poor'},
        {'cLo': 1601.0, 'cHi': 2000.0, 'iLo': 401, 'iHi': 500, 'cat': 'Severe'}
    ],
    'co': [
        # CPCB CO is measured in mg/m3 (8-hour average)
        {'cLo': 0.0, 'cHi': 1.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 1.1, 'cHi': 2.0, 'iLo': 51, 'iHi': 100, 'cat': 'Satisfactory'},
        {'cLo': 2.1, 'cHi': 10.0, 'iLo': 101, 'iHi': 200, 'cat': 'Moderate'},
        {'cLo': 10.1, 'cHi': 17.0, 'iLo': 201, 'iHi': 300, 'cat': 'Poor'},
        {'cLo': 17.1, 'cHi': 34.0, 'iLo': 301, 'iHi': 400, 'cat': 'Very Poor'},
        {'cLo': 34.1, 'cHi': 50.0, 'iLo': 401, 'iHi': 500, 'cat': 'Severe'}
    ],
    'o3': [
        {'cLo': 0.0, 'cHi': 50.0, 'iLo': 0, 'iHi': 50, 'cat': 'Good'},
        {'cLo': 51.0, 'cHi': 100.0, 'iLo': 51, 'iHi': 100, 'cat': 'Satisfactory'},
        {'cLo': 101.0, 'cHi': 168.0, 'iLo': 101, 'iHi': 200, 'cat': 'Moderate'},
        {'cLo': 169.0, 'cHi': 208.0, 'iLo': 201, 'iHi': 300, 'cat': 'Poor'},
        {'cLo': 209.0, 'cHi': 748.0, 'iLo': 301, 'iHi': 400, 'cat': 'Very Poor'},
        {'cLo': 749.0, 'cHi': 1000.0, 'iLo': 401, 'iHi': 500, 'cat': 'Severe'}
    ]
}


def calc_aqi_subindex(pollutant: str, conc: float, standard: str = "EPA") -> Dict[str, Any]:
    """
    Interpolates AQI sub-index for a given pollutant and concentration.
    standard: 'EPA' (US EPA) or 'CPCB' (Indian National AQI)
    """
    p_key = pollutant.lower().replace('.', '').replace('_', '')
    if p_key in ('pm25', 'pm2_5'):
        p_key = 'pm25'
    elif p_key in ('pm10', 'pm_10'):
        p_key = 'pm10'

    std_table = CPCB_BREAKPOINTS if standard.upper() == 'CPCB' else EPA_BREAKPOINTS
    bps = std_table.get(p_key, std_table['pm25'])
    c = max(0.0, float(conc))

    for bp in bps:
        if bp['cLo'] <= c <= bp['cHi']:
            aqi = round(((bp['iHi'] - bp['iLo']) / (bp['cHi'] - bp['cLo'])) * (c - bp['cLo']) + bp['iLo'])
            return {
                'aqi': int(min(500, max(0, aqi))),
                'category': bp['cat'],
                'standard': standard.upper(),
                'pollutant': p_key,
                'breakpoint_low': bp['cLo'],
                'breakpoint_high': bp['cHi']
            }

    # Exceeds maximum scale: clamp to 500
    last = bps[-1]
    return {
        'aqi': 500,
        'category': last['cat'],
        'standard': standard.upper(),
        'pollutant': p_key,
        'breakpoint_low': last['cLo'],
        'breakpoint_high': last['cHi']
    }
