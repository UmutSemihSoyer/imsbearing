"""
IMS ISO 10816-3 / ISO 20816 Vibration Severity Compliance Evaluator
Classifies machine vibration severity into ISO zones (Zone A: Good, Zone B: Satisfactory, Zone C: Unsatisfactory, Zone D: Unacceptable).
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class ISO10816StandardEvaluator:
    """
    Evaluates vibration velocity RMS (mm/s) against ISO 10816-3 Class II (medium-sized industrial machines 15-75 kW).
    """

    ISO_LIMITS = {
        "zone_a_good": 1.4,          # mm/s RMS
        "zone_b_satisfactory": 2.8,  # mm/s RMS
        "zone_c_unsatisfactory": 4.5 # mm/s RMS
        # Zone D > 4.5 mm/s
    }

    def evaluate_vibration_severity(self, acceleration_rms_g: float, shaft_speed_rpm: float = 1800.0) -> Dict[str, Any]:
        """
        Converts acceleration RMS (g) to velocity RMS (mm/s) and classifies ISO 10816-3 Zone.
        V_rms (mm/s) approx = (a_rms * 9.81 * 1000) / (2 * pi * f_shaft)
        """
        f_shaft_hz = shaft_speed_rpm / 60.0
        v_rms_mms = float((acceleration_rms_g * 9.81 * 1000.0) / (2.0 * np.pi * f_shaft_hz))

        if v_rms_mms <= self.ISO_LIMITS["zone_a_good"]:
            zone = "Zone A: Good"
            status = "NORMAL"
            desc = "Newly commissioned equipment. Operating within optimal limits."
        elif v_rms_mms <= self.ISO_LIMITS["zone_b_satisfactory"]:
            zone = "Zone B: Satisfactory"
            status = "ACCEPTABLE"
            desc = "Acceptable for long-term unrestricted operation."
        elif v_rms_mms <= self.ISO_LIMITS["zone_c_unsatisfactory"]:
            zone = "Zone C: Unsatisfactory"
            status = "WARNING"
            desc = "Unsatisfactory for continuous operation. Schedule maintenance soon."
        else:
            zone = "Zone D: Unacceptable"
            status = "CRITICAL"
            desc = "Vibration severity causes damage. STOP MACHINE IMMEDIATELY."

        return {
            "acceleration_rms_g": round(acceleration_rms_g, 4),
            "velocity_rms_mms": round(v_rms_mms, 2),
            "iso_zone": zone,
            "operational_status": status,
            "iso_recommendation": desc
        }

if __name__ == "__main__":
    iso = ISO10816StandardEvaluator()
    print("Baseline Healthy ISO Check:", iso.evaluate_vibration_severity(0.02, 1800))
    print("Warning Level ISO Check:", iso.evaluate_vibration_severity(0.08, 1800))
    print("Critical Level ISO Check:", iso.evaluate_vibration_severity(0.20, 1800))
