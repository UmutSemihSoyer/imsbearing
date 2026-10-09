"""
IMS Haptic Feedback Gloves Bio-Tactile Engine
Translates high-frequency bearing micro-vibrations into bio-tactile force feedback signals for VR gloves.
"""

import os
import sys
import numpy as np
from typing import Dict, Any, List

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class HapticFeedbackGloveSimulator:
    """
    Translates vibration spectrum into 5-fingertip haptic actuator pulse frequencies (Hz) and amplitudes.
    """

    def generate_haptic_glove_pulses(self, rms_g: float, kurtosis: float) -> Dict[str, Any]:
        """
        Calculates haptic glove vibration frequencies for Thumb, Index, Middle, Ring, Pinky.
        """
        base_freq_hz = float(np.clip(100.0 + rms_g * 200.0, 10.0, 300.0))
        actuator_amplitude = float(np.clip(kurtosis / 10.0, 0.1, 1.0))

        fingertip_signals = {
            "thumb": {"freq_hz": round(base_freq_hz, 1), "amplitude": round(actuator_amplitude, 2)},
            "index": {"freq_hz": round(base_freq_hz * 1.2, 1), "amplitude": round(actuator_amplitude, 2)},
            "middle": {"freq_hz": round(base_freq_hz, 1), "amplitude": round(actuator_amplitude, 2)},
            "ring": {"freq_hz": round(base_freq_hz * 0.8, 1), "amplitude": round(actuator_amplitude, 2)},
            "pinky": {"freq_hz": round(base_freq_hz * 0.8, 1), "amplitude": round(actuator_amplitude, 2)}
        }

        return {
            "glove_model": "SenseGlove DK1 / Meta Haptic Tactile Glove",
            "tactile_roughness_feel": "SEVERE_SPALLING_PITTING_FEEL" if kurtosis > 5.0 else "SMOOTH_SURFACE_FEEL",
            "fingertip_actuators": fingertip_signals
        }

if __name__ == "__main__":
    haptic = HapticFeedbackGloveSimulator()
    print(haptic.generate_haptic_glove_pulses(rms_g=0.35, kurtosis=7.4))
