"""
IMS Infrared Thermal Camera & Vibration Pixel-Level Fusion Engine
Correlates 2D thermal IR hotspot matrix with 1D accelerometer RMS trends for early overheating detection.
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class ThermalVibrationFusionEngine:
    """
    Correlates infrared thermal camera images with vibration RMS spectra.
    """

    def fuse_thermal_image_with_vibration(self, thermal_matrix_c: np.ndarray, rms_g: float) -> Dict[str, Any]:
        """
        Calculates peak hotspot temperature, thermal spatial variance, and thermal-vibration risk score.
        """
        max_temp = float(np.max(thermal_matrix_c))
        mean_temp = float(np.mean(thermal_matrix_c))
        hotspot_var = float(np.var(thermal_matrix_c))

        # Thermal-Vibration Fused Risk Score
        tv_risk_score = float((max_temp - 30.0) * 1.5 + (rms_g * 100.0))

        if tv_risk_score > 90.0:
            status = "CRITICAL - THERMAL & MECHANICAL OVERHEAT"
        elif tv_risk_score > 45.0:
            status = "WARNING - ELEVATED TEMPERATURE & VIBRATION"
        else:
            status = "NORMAL OPERATING CONDITION"

        return {
            "peak_hotspot_temp_c": round(max_temp, 2),
            "mean_surface_temp_c": round(mean_temp, 2),
            "thermal_spatial_variance": round(hotspot_var, 2),
            "vibration_rms_g": rms_g,
            "tv_fused_risk_score": round(tv_risk_score, 2),
            "fused_status": status
        }

if __name__ == "__main__":
    fusion = ThermalVibrationFusionEngine()
    
    # 16x16 Thermal IR Matrix (Healthy)
    healthy_thermal = 35.0 + 2.0 * np.random.randn(16, 16)
    print("Healthy Thermal-Vibration Fusion:", fusion.fuse_thermal_image_with_vibration(healthy_thermal, 0.06))

    # 16x16 Thermal IR Matrix (Overheating Hotspot at Outer Race)
    degraded_thermal = 35.0 + 2.0 * np.random.randn(16, 16)
    degraded_thermal[7:10, 7:10] += 45.0 # Hotspot 80°C
    print("Degraded Thermal-Vibration Fusion:", fusion.fuse_thermal_image_with_vibration(degraded_thermal, 0.58))
