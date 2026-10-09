"""
IMS Prescriptive Maintenance Engine
Generates actionable operational guidance (e.g. speed reduction, load shifting) to maximize component life until planned shutdown.
"""

import os
import sys
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class PrescriptiveMaintenanceEngine:
    """
    Recommends operational load & speed adjustments to stretch RUL to target maintenance window.
    """

    def recommend_prescriptive_action(self, current_rul_hours: float, target_shutdown_hours: float = 48.0,
                                     current_rpm: float = 2000.0) -> Dict[str, Any]:
        """
        Calculates required speed/load derating factor to delay bearing failure.
        """
        if current_rul_hours >= target_shutdown_hours:
            return {
                "action_type": "NO_ACTION_REQUIRED",
                "recommended_rpm": current_rpm,
                "derating_percentage": 0.0,
                "projected_rul_hours": current_rul_hours,
                "guidance_text": "Current RUL is sufficient to reach the next planned maintenance window."
            }

        # Lifespan ratio L ~ (1 / RPM) * (1 / P^3.33)
        # To extend life from current_rul to target_shutdown:
        required_life_extension_factor = target_shutdown_hours / max(0.1, current_rul_hours)
        
        # Speed derating calculation
        new_rpm = max(800.0, current_rpm / (required_life_extension_factor ** 0.5))
        derating_pct = round(((current_rpm - new_rpm) / current_rpm) * 100.0, 1)

        return {
            "action_type": "DERATE_OPERATIONAL_LOAD",
            "current_rpm": current_rpm,
            "recommended_rpm": round(new_rpm, 0),
            "derating_percentage": derating_pct,
            "original_rul_hours": round(current_rul_hours, 1),
            "projected_rul_hours": round(target_shutdown_hours, 1),
            "guidance_text": f"Reduce motor RPM by {derating_pct}% (from {int(current_rpm)} to {int(new_rpm)} RPM) to delay catastrophic failure until planned shutdown."
        }

if __name__ == "__main__":
    engine = PrescriptiveMaintenanceEngine()
    rec = engine.recommend_prescriptive_action(current_rul_hours=18.0, target_shutdown_hours=48.0)
    print("Prescriptive Maintenance Advice:", rec)
