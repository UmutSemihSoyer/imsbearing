"""
IMS Photonic Computing & Fiber Bragg Grating (FBG) Optical Sensor Engine
Measures immune-to-EMI optical wavelength shift (nm) for sub-microsecond strain measurements.
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class PhotonicFBGSensorEngine:
    """
    Simulates Fiber Bragg Grating (FBG) optical strain & temperature sensor wavelength shift.
    """

    # Central Bragg Wavelength lambda_0 = 1550 nm
    LAMBDA_0_NM = 1550.0

    def measure_fbg_wavelength_shift(self, strain_microstrain: float, temp_change_c: float) -> Dict[str, Any]:
        """
        Calculates Bragg wavelength shift delta_lambda (nm).
        delta_lambda = lambda_0 * (1 - p_e) * strain + K_T * delta_T
        """
        # Strain sensitivity ~ 1.2 pm/microstrain, Temperature sensitivity ~ 10 pm/C
        delta_lambda_nm = (strain_microstrain * 1.2e-3) + (temp_change_c * 10e-3)
        measured_wavelength_nm = self.LAMBDA_0_NM + delta_lambda_nm

        return {
            "sensor_technology": "Fiber Bragg Grating (FBG) Optical Sensing",
            "emi_immunity": "100% IMMUNE_TO_ELECTROMAGNETIC_INTERFERENCE",
            "base_wavelength_nm": self.LAMBDA_0_NM,
            "measured_wavelength_nm": round(float(measured_wavelength_nm), 4),
            "wavelength_shift_pm": round(float(delta_lambda_nm * 1000.0), 2)
        }

if __name__ == "__main__":
    fbg = PhotonicFBGSensorEngine()
    print(fbg.measure_fbg_wavelength_shift(strain_microstrain=250.0, temp_change_c=12.5))
