"""
IMS Multi-Unit Converter Engine (Metric vs Imperial)
Provides instant unit conversions for acceleration (g, m/s2), velocity (mm/s, in/s), speed (RPM, Hz), and load (kN, lbs).
"""

import os
import sys
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class MultiUnitConverter:
    """
    Bi-directional unit converter for vibration and mechanical engineering metrics.
    """

    GRAVITY_MS2 = 9.80665

    @staticmethod
    def g_to_ms2(g_val: float) -> float:
        """Converts acceleration from g to m/s^2."""
        return float(g_val * MultiUnitConverter.GRAVITY_MS2)

    @staticmethod
    def ms2_to_g(ms2_val: float) -> float:
        """Converts acceleration from m/s^2 to g."""
        return float(ms2_val / MultiUnitConverter.GRAVITY_MS2)

    @staticmethod
    def rpm_to_hz(rpm: float) -> float:
        """Converts shaft speed from RPM to Hz (rev/sec)."""
        return float(rpm / 60.0)

    @staticmethod
    def hz_to_rpm(hz: float) -> float:
        """Converts shaft speed from Hz to RPM."""
        return float(hz * 60.0)

    @staticmethod
    def kn_to_lbs(kn_val: float) -> float:
        """Converts radial load from kN to pounds-force (lbs)."""
        return float(kn_val * 224.809)

    @staticmethod
    def mms_to_ips(mms_val: float) -> float:
        """Converts velocity from mm/s to inches per second (ips)."""
        return float(mms_val / 25.4)

    def convert_telemetry_units(self, rms_g: float, rpm: float, load_kn: float) -> Dict[str, Any]:
        """Returns comprehensive multi-unit dictionary."""
        return {
            "acceleration": {
                "g": round(rms_g, 4),
                "m_s2": round(self.g_to_ms2(rms_g), 4)
            },
            "speed": {
                "rpm": round(rpm, 1),
                "hz": round(self.rpm_to_hz(rpm), 2),
                "rad_s": round(self.rpm_to_hz(rpm) * 2 * 3.14159, 2)
            },
            "radial_load": {
                "kn": round(load_kn, 2),
                "lbs": round(self.kn_to_lbs(load_kn), 1)
            }
        }

if __name__ == "__main__":
    converter = MultiUnitConverter()
    print("Multi-Unit Converted Telemetry:", converter.convert_telemetry_units(0.12, 1800.0, 6.5))
