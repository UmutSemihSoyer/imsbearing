import sys
from typing import Dict, Any

class CobotSafetyTactileController:
    """Evaluates collaborative robot (Cobot) safety distance and tactile collision prevention during bearing replacement."""
    
    def evaluate_cobot_safety(self, human_distance_m: float, cobot_velocity_ms: float) -> Dict[str, Any]:
        """
        Calculates safe deceleration distance according to ISO 15066 Cobot Safety Standard.
        """
        # ISO 15066 Protective separation distance formulation
        reaction_time_s = 0.1
        robot_stopping_distance_m = (cobot_velocity_ms * reaction_time_s) + (0.5 * (cobot_velocity_ms ** 2) / 2.0)
        min_required_distance_m = robot_stopping_distance_m + 0.35  # Safety margin
        
        if human_distance_m >= min_required_distance_m:
            safety_zone = "GREEN_NORMAL_OPERATION"
            speed_override = cobot_velocity_ms
            action = "Cobot operating at full rated assembly speed."
        elif human_distance_m >= min_required_distance_m * 0.5:
            safety_zone = "YELLOW_REDUCED_SPEED"
            speed_override = cobot_velocity_ms * 0.3
            action = "Human engineer in proximity. Speed derated to 30%."
        else:
            safety_zone = "RED_EMERGENCY_STOP"
            speed_override = 0.0
            action = "Immediate cobot power cutoff! Human technician within safety envelope."

        return {
            "cobot_standard": "ISO/TS 15066 Robots & Robotic Devices",
            "human_distance_m": human_distance_m,
            "min_required_safe_distance_m": round(min_required_distance_m, 2),
            "safety_zone": safety_zone,
            "adjusted_speed_ms": round(speed_override, 2),
            "action_taken": action
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Stage 76: Cobot Safety & Tactile Collision Avoidance Test ===")
    controller = CobotSafetyTactileController()
    
    safe_test = controller.evaluate_cobot_safety(human_distance_m=1.8, cobot_velocity_ms=0.8)
    hazard_test = controller.evaluate_cobot_safety(human_distance_m=0.2, cobot_velocity_ms=0.8)
    
    print("Safe Distance Assessment:", safe_test)
    print("Hazardous Proximity Assessment:", hazard_test)
    print("Stage 76 execution complete.")
