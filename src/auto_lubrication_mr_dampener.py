"""
IMS Self-Healing Hardware: Auto-Lubricator & Magnetorheological (MR) Fluid Damper
Triggers microliter lubricant injection and adjusts MR fluid magnetic field to damp severe vibration spikes.
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class SelfHealingHardwareController:
    """
    Controls micro-lubrication injection and Magnetorheological (MR) damping magnetic field.
    """

    def Trigger_self_healing_response(self, rms_g: float, temp_c: float) -> Dict[str, Any]:
        """
        Calculates required lubricant injection volume (uL) and MR damper current (Amperes).
        """
        # Inject lubricant if temperature > 55 C or RMS > 0.20 g
        inject_lubricant = bool(temp_c > 55.0 or rms_g > 0.20)
        injection_volume_ul = float(np.clip((rms_g * 500.0) + (temp_c - 35.0) * 10.0, 0.0, 1000.0)) if inject_lubricant else 0.0

        # Adjust Magnetorheological Damper current (0.0 to 2.0 Amperes -> alters fluid viscosity)
        mr_current_amp = float(np.clip(rms_g * 3.5, 0.0, 2.0))

        return {
            "auto_lubricator_active": inject_lubricant,
            "lubricant_injected_microliters": round(injection_volume_ul, 1),
            "mr_damper_current_amperes": round(mr_current_amp, 2),
            "vibration_damping_reduction_pct": round(min(45.0, mr_current_amp * 22.5), 1)
        }

if __name__ == "__main__":
    controller = SelfHealingHardwareController()
    print(controller.Trigger_self_healing_response(rms_g=0.45, temp_c=68.0))
