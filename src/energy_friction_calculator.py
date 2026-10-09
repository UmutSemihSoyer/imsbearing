"""
IMS Friction Loss & Extra Energy Consumption Engine (Green AI)
Calculates additional friction power loss (kWh) caused by degraded bearing raceway surface roughness.
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import PITCH_DIAMETER_INCH

class EnergyFrictionCalculator:
    """
    Estimates wasted friction energy (kWh) and excess electricity cost resulting from bearing degradation.
    """

    def __init__(self, electricity_cost_per_kwh_usd: float = 0.15):
        self.kwh_cost = electricity_cost_per_kwh_usd

    def calculate_energy_waste(self, rms_g: float, rpm: float = 2000.0,
                                radial_load_kn: float = 6.0, operating_hours: float = 24.0) -> Dict[str, Any]:
        """
        Calculates wasted energy (kWh) caused by elevated bearing friction torque.
        """
        # Baseline healthy friction coefficient mu_0 = 0.0015
        # Damaged bearing friction coefficient mu increases with RMS vibration
        mu_friction = float(0.0015 + 0.015 * (rms_g / 0.10))

        d_pitch_m = PITCH_DIAMETER_INCH * 0.0254
        load_n = radial_load_kn * 1000.0

        # Friction Torque M = mu * P * (d / 2) (Nm)
        friction_torque_nm = mu_friction * load_n * (d_pitch_m / 2.0)

        # Power Loss P_loss = M * omega (Watts)
        omega = (rpm / 60.0) * (2.0 * np.pi)
        power_loss_watts = friction_torque_nm * omega

        # Wasted energy (kWh) over operating hours
        wasted_kwh = float((power_loss_watts / 1000.0) * operating_hours)
        excess_cost_usd = float(wasted_kwh * self.kwh_cost)

        return {
            "vibration_rms_g": rms_g,
            "friction_coefficient": round(mu_friction, 5),
            "friction_power_loss_watts": round(power_loss_watts, 2),
            "wasted_energy_kwh": round(wasted_kwh, 3),
            "excess_electricity_cost_usd": round(excess_cost_usd, 2)
        }

if __name__ == "__main__":
    calc = EnergyFrictionCalculator(electricity_cost_per_kwh_usd=0.15)
    
    # Healthy Baseline Energy Loss
    print("Healthy Bearing Friction:", calc.calculate_energy_waste(rms_g=0.05, operating_hours=720))

    # Damaged Bearing Energy Loss (1 month)
    print("Degraded Bearing Friction:", calc.calculate_energy_waste(rms_g=0.55, operating_hours=720))
