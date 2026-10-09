"""
IMS Multi-Sensor Fusion Engine
Fuses vibration acceleration, housing temperature, acoustic emission (AE), and oil debris data for multi-physics fault diagnosis.
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class MultiSensorFusionEngine:
    """
    Implements weighted multi-sensor fusion combining vibration, thermal, acoustic emission, and oil condition telemetry.
    """

    # Sensor baseline & degradation bounds
    SENSOR_BOUNDS = {
        "vibration_rms": {"healthy": 0.08, "warning": 0.25, "critical": 0.50, "weight": 0.40},
        "temperature_c": {"healthy": 35.0, "warning": 65.0, "critical": 85.0, "weight": 0.25},
        "acoustic_emission": {"healthy": 0.05, "warning": 0.20, "critical": 0.45, "weight": 0.20},
        "oil_debris_ppm": {"healthy": 10.0, "warning": 50.0, "critical": 120.0, "weight": 0.15}
    }

    def compute_sensor_health(self, val: float, bounds: dict) -> float:
        """Normalizes a single sensor reading to a 0.0 (failed) to 1.0 (healthy) scale."""
        h = bounds["healthy"]
        c = bounds["critical"]
        if val <= h:
            return 1.0
        elif val >= c:
            return 0.0
        else:
            return float(1.0 - (val - h) / (c - h))

    def fuse_telemetry(self, vibration_rms: float, temperature_c: float,
                       acoustic_emission: float, oil_debris_ppm: float) -> Dict[str, Any]:
        """
        Fuses 4 sensor channels into a single Multi-Physics Fused Health Index and identifies primary root cause.
        """
        hi_vib = self.compute_sensor_health(vibration_rms, self.SENSOR_BOUNDS["vibration_rms"])
        hi_temp = self.compute_sensor_health(temperature_c, self.SENSOR_BOUNDS["temperature_c"])
        hi_ae = self.compute_sensor_health(acoustic_emission, self.SENSOR_BOUNDS["acoustic_emission"])
        hi_oil = self.compute_sensor_health(oil_debris_ppm, self.SENSOR_BOUNDS["oil_debris_ppm"])

        # Weighted Sensor Fusion Formula
        w_vib = self.SENSOR_BOUNDS["vibration_rms"]["weight"]
        w_temp = self.SENSOR_BOUNDS["temperature_c"]["weight"]
        w_ae = self.SENSOR_BOUNDS["acoustic_emission"]["weight"]
        w_oil = self.SENSOR_BOUNDS["oil_debris_ppm"]["weight"]

        fused_hi = (w_vib * hi_vib) + (w_temp * hi_temp) + (w_ae * hi_ae) + (w_oil * hi_oil)

        # Identify dominant degradation mode
        scores = {
            "Mechanical Spalling (Vibration)": 1.0 - hi_vib,
            "Thermal Overheating (Temperature)": 1.0 - hi_temp,
            "Micro-Crack AE Emission": 1.0 - hi_ae,
            "Lubricant Degradation (Oil Debris)": 1.0 - hi_oil
        }
        primary_fault = max(scores, key=scores.get)

        if fused_hi > 0.75:
            health_state = "NORMAL"
        elif fused_hi > 0.35:
            health_state = "WARNING"
        else:
            health_state = "CRITICAL"

        return {
            "fused_health_index": round(float(fused_hi), 4),
            "health_state": health_state,
            "primary_fault_mode": primary_fault,
            "sensor_health_breakdown": {
                "vibration_hi": round(hi_vib, 4),
                "temperature_hi": round(hi_temp, 4),
                "acoustic_emission_hi": round(hi_ae, 4),
                "oil_debris_hi": round(hi_oil, 4)
            }
        }

if __name__ == "__main__":
    fusion = MultiSensorFusionEngine()
    
    # Test healthy
    healthy_res = fusion.fuse_telemetry(vibration_rms=0.07, temperature_c=36.0, acoustic_emission=0.04, oil_debris_ppm=8.0)
    print("Healthy Multi-Sensor Fusion:", healthy_res)

    # Test degraded
    degraded_res = fusion.fuse_telemetry(vibration_rms=0.45, temperature_c=72.0, acoustic_emission=0.38, oil_debris_ppm=95.0)
    print("Degraded Multi-Sensor Fusion:", degraded_res)
