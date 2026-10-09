import sys
from typing import Dict, Any

class UAVVTOLMotorBearingAnalyzer:
    """Ek J: UAV & VTOL Electric Motor Bearings Vertical Adaptation."""
    
    def evaluate_vtol_motor_bearing(
        self,
        motor_rpm: float = 8500.0,
        motor_temp_c: float = 95.0,
        wind_gust_knots: float = 28.0,
        battery_soc_pct: float = 75.0
    ) -> Dict[str, Any]:
        """
        J.1: eVTOL urban air taxi brushless motor thermal spike & wind gust stress.
        J.2: Bearing friction coefficient impact on flight range & battery consumption.
        """
        # Thermal & wind gust load multiplier
        wind_stress_factor = 1.0 + (wind_gust_knots / 50.0) * 0.4
        thermal_stress_factor = 1.0 + max(0.0, (motor_temp_c - 75.0) / 50.0)
        
        combined_stress = wind_stress_factor * thermal_stress_factor
        
        # Friction penalty on eVTOL battery flight range
        friction_range_loss_pct = (combined_stress - 1.0) * 8.5
        remaining_flight_range_km = 45.0 * (1.0 - (friction_range_loss_pct / 100.0))

        return {
            "vertical_domain": "EVTOL_UAV_BRUSHLESS_MOTOR",
            "motor_rpm": motor_rpm,
            "motor_temp_c": motor_temp_c,
            "wind_gust_knots": wind_gust_knots,
            "combined_motor_stress_index": round(combined_stress, 3),
            "friction_battery_range_penalty_pct": round(friction_range_loss_pct, 2),
            "safe_remaining_flight_range_km": round(remaining_flight_range_km, 1),
            "vtol_flight_cleared": remaining_flight_range_km > 15.0
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Appendix J: UAV eVTOL Motor Bearing Test ===")
    analyzer = UAVVTOLMotorBearingAnalyzer()
    res = analyzer.evaluate_vtol_motor_bearing()
    print("eVTOL UAV Output:", res)
    print("Appendix J execution complete.")
