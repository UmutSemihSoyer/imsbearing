"""
IMS Dynamic Load & Mechanical Stress Estimator
Estimates equivalent radial load, Hertzian contact stress, and dynamic fatigue factor under varying load conditions.
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import N_ROLLERS, ROLLER_DIAMETER_INCH, PITCH_DIAMETER_INCH

class DynamicLoadStressEstimator:
    """
    Computes Hertzian contact stress and dynamic load rating adjustments for Rexnord ZA-2115 bearing.
    """

    def __init__(self, static_radial_load_kn: float = 6.0):
        self.base_load_kn = static_radial_load_kn

    def estimate_dynamic_stress(self, rpm: float, rms_g: float) -> Dict[str, Any]:
        """
        Calculates dynamic shock load multiplier, contact stress (MPa), and L10h life adjustment factor.
        """
        # Dynamic impact factor based on RMS vibration acceleration
        dynamic_factor = float(1.0 + 2.5 * rms_g)
        P_equivalent_kn = self.base_load_kn * dynamic_factor

        # Hertzian Contact Stress Estimation (Approximate roller contact formula)
        # Convert inches to meters
        d_m = ROLLER_DIAMETER_INCH * 0.0254
        D_m = PITCH_DIAMETER_INCH * 0.0254
        
        # Max load per roller Q_max (kN)
        q_max_kn = (5.0 * P_equivalent_kn) / N_ROLLERS
        
        # Contact Stress sigma_c (MPa) proportional to sqrt(Q / d)
        contact_stress_mpa = float(250.0 * np.sqrt((q_max_kn * 1000.0) / (d_m * 1000.0 * 25.0)))

        # ISO 281 L10h Rating Life Factor (L10h ~ (C / P)^3 * (10^6 / (60 * n)))
        C_basic_rating_kn = 45.0  # Basic dynamic load rating for ZA-2115
        l10_hours = float(((C_basic_rating_kn / P_equivalent_kn) ** 3.33) * (1e6 / (60.0 * rpm)))

        stress_level = "CRITICAL" if contact_stress_mpa > 1500.0 else ("ELEVATED" if contact_stress_mpa > 1000.0 else "NORMAL")

        return {
            "rpm": rpm,
            "vibration_rms_g": rms_g,
            "dynamic_shock_factor": round(dynamic_factor, 3),
            "equivalent_radial_load_kn": round(P_equivalent_kn, 3),
            "peak_hertzian_stress_mpa": round(contact_stress_mpa, 1),
            "estimated_l10h_life_hours": round(l10_hours, 1),
            "stress_level": stress_level
        }

if __name__ == "__main__":
    estimator = DynamicLoadStressEstimator(static_radial_load_kn=6.0)
    
    # Baseline normal stress
    print("Normal Load Conditions:", estimator.estimate_dynamic_stress(rpm=2000, rms_g=0.08))

    # Severe vibration shock stress
    print("Severe Shock Conditions:", estimator.estimate_dynamic_stress(rpm=2000, rms_g=0.65))
