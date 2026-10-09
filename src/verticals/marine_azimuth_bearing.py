import numpy as np
import sys
from typing import Dict, Any

class MarineAzimuthBearingAnalyzer:
    """Ek H: Marine Shaft & Azimuth Thrusters Vertical Adaptation."""
    
    def analyze_marine_stern_tube(
        self,
        raw_vibration: np.ndarray,
        steering_angle_deg: float = 45.0,
        sea_state_scale_douglas: int = 4
    ) -> Dict[str, Any]:
        """
        H.1: Ocean wave slam shocks vs stern tube bearing wear isolation.
        H.2: Azimuth 360-degree thruster gyroscopic load vector calculation.
        """
        rms_g = float(np.sqrt(np.mean(raw_vibration ** 2)))
        
        # Sea state wave shock compensation factor
        wave_slam_compensation = max(1.0, sea_state_scale_douglas * 0.25)
        isolated_bearing_vibration = rms_g / wave_slam_compensation
        
        # Azimuth steering gyroscopic load (N)
        gyro_load_kn = 150.0 * np.sin(np.radians(steering_angle_deg))

        return {
            "vertical_domain": "MARINE_STERN_TUBE_AZIMUTH_THRUSTER",
            "sea_state_scale_douglas": sea_state_scale_douglas,
            "steering_angle_deg": steering_angle_deg,
            "wave_slam_compensation_factor": round(wave_slam_compensation, 2),
            "isolated_bearing_rms_g": round(isolated_bearing_vibration, 4),
            "azimuth_steering_gyro_load_kn": round(gyro_load_kn, 1),
            "marine_inspection_status": "NORMAL_SEA_PASSAGE" if isolated_bearing_vibration < 0.25 else "CHECK_STERN_TUBE_SEAL"
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Appendix H: Marine Stern Tube & Azimuth Thruster Test ===")
    analyzer = MarineAzimuthBearingAnalyzer()
    sig = np.random.normal(0, 0.3, 2048)
    res = analyzer.analyze_marine_stern_tube(sig)
    print("Marine Azimuth Output:", res)
    print("Appendix H execution complete.")
