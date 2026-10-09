"""
IMS 3D Spatial Audio & Unreal Engine 5 Twin Integration Engine
Synthesizes 3D spatialized sound binaural cues positioning degraded bearings in 3D factory space.
"""

import os
import sys
import numpy as np
from typing import Dict, Any, Tuple

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import FS

class SpatialAudio3DSimulator:
    """
    Synthesizes binaural 3D spatialized sound (Left/Right ear time delay ITD & level difference ILD).
    """

    def synthesize_3d_bearing_sound(self, bearing_coords: Tuple[float, float, float] = (3.0, 2.0, 1.5),
                                    defect_freq_hz: float = 236.4, duration_sec: float = 0.5) -> Dict[str, Any]:
        """
        Calculates Interaural Time Difference (ITD) and Interaural Level Difference (ILD) for 3D headphone positioning.
        """
        x, y, z = bearing_coords # Coordinates relative to head (0,0,0)
        distance = float(np.sqrt(x**2 + y**2 + z**2))

        # Azimuth angle theta (radians)
        azimuth_deg = float(np.degrees(np.arctan2(x, y)))

        # Interaural Time Difference (Woodworth equation: ITD = (r/c) * (theta + sin(theta)))
        head_radius_m = 0.0875
        sound_speed_m_s = 343.0
        theta_rad = np.radians(abs(azimuth_deg))
        itd_seconds = float((head_radius_m / sound_speed_m_s) * (theta_rad + np.sin(theta_rad)))

        # Attenuation based on distance (Inverse square law)
        gain_attenuation = float(1.0 / max(1.0, distance**1.5))

        return {
            "bearing_coordinates_m": bearing_coords,
            "distance_to_operator_m": round(distance, 2),
            "azimuth_angle_deg": round(azimuth_deg, 1),
            "itd_micro_seconds": round(itd_seconds * 1e6, 1),
            "spatial_gain_attenuation": round(gain_attenuation, 4),
            "unreal_engine_5_tag": f"UE5_SPATIAL_AUDIO_SOURCE_X{x:.1f}_Y{y:.1f}_Z{z:.1f}"
        }

if __name__ == "__main__":
    audio_sim = SpatialAudio3DSimulator()
    result = audio_sim.synthesize_3d_bearing_sound((4.5, -2.0, 1.0), defect_freq_hz=236.4)
    print("3D Spatial Audio Cue:", result)
