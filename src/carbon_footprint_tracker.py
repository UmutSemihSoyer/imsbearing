"""
IMS CO2 Carbon Footprint & Green AI Sustainability Tracker
Calculates additional carbon emissions (kg CO2) caused by inefficient, degraded machinery.
"""

import os
import sys
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.energy_friction_calculator import EnergyFrictionCalculator

class CarbonFootprintTracker:
    """
    Computes environmental CO2 impact and Green Manufacturing Index for plant machinery.
    """

    def __init__(self, grid_co2_factor_kg_per_kwh: float = 0.475): # Global avg grid intensity
        self.co2_factor = grid_co2_factor_kg_per_kwh
        self.energy_calc = EnergyFrictionCalculator()

    def calculate_carbon_footprint(self, rms_g: float, operating_hours: float = 720.0) -> Dict[str, Any]:
        """
        Calculates excess CO2 emissions (kg CO2) resulting from degraded bearing friction.
        """
        energy_res = self.energy_calc.calculate_energy_waste(rms_g=rms_g, operating_hours=operating_hours)
        wasted_kwh = energy_res["wasted_energy_kwh"]

        excess_co2_kg = float(wasted_kwh * self.co2_factor)

        # Green Manufacturing Index (100 = Optimal Efficiency, < 50 = Severe CO2 Waste)
        green_index = float(max(0.0, 100.0 - (excess_co2_kg / 10.0)))

        return {
            "vibration_rms_g": rms_g,
            "wasted_kwh": wasted_kwh,
            "excess_co2_emissions_kg": round(excess_co2_kg, 2),
            "green_manufacturing_index": round(green_index, 1),
            "sustainability_rating": "EXCELLENT" if green_index > 85 else ("MODERATE" if green_index > 50 else "POOR - HIGH EMISSIONS")
        }

if __name__ == "__main__":
    tracker = CarbonFootprintTracker()
    print("Healthy CO2 Impact:", tracker.calculate_carbon_footprint(rms_g=0.05, operating_hours=720))
    print("Degraded CO2 Impact:", tracker.calculate_carbon_footprint(rms_g=0.55, operating_hours=720))
