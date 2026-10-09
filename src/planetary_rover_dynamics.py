import sys
from typing import Dict, Any

class PlanetaryRoverDynamicsModel:
    """Estimates bearing life for space exploration rovers (Mars / Moon) under extreme thermal swings and dust."""
    
    def calculate_extraterrestrial_wear(
        self,
        ambient_temp_c: float = -120.0,
        regolith_dust_ppm: float = 450.0,
        radiation_flux_krad: float = 15.0
    ) -> Dict[str, Any]:
        """
        Calculates cryogenic clearance contraction, abrasive dust wear coefficient, and RUL factor.
        """
        # Thermal contraction rate of 52100 steel (11.5 e-6 / K)
        temp_delta = ambient_temp_c - 20.0
        clearance_shrinkage_um = abs(temp_delta) * 0.08  # Micro-meter shrinkage
        
        # Abrasive dust factor
        abrasive_wear_rate = (regolith_dust_ppm / 100.0) * 1.8
        
        # Combined life derating multiplier
        if ambient_temp_c < -100.0:
            lubricant_state = "SOLIDIFIED_CRYOGENIC_PASTE"
            friction_multiplier = 4.5
        else:
            lubricant_state = "LIQUID_FLUORINATED_SYNTHETIC"
            friction_multiplier = 1.2
            
        rover_rul_hours = 10000.0 / (friction_multiplier + abrasive_wear_rate)
        
        return {
            "planet_target": "MARS_PERSEVERANCE_CLASS",
            "ambient_temp_c": ambient_temp_c,
            "clearance_shrinkage_um": round(clearance_shrinkage_um, 2),
            "regolith_dust_ppm": regolith_dust_ppm,
            "lubricant_state": lubricant_state,
            "abrasive_wear_index": round(abrasive_wear_rate, 2),
            "rover_bearing_rul_hours": round(rover_rul_hours, 1)
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Stage 69: Mars Rover & Planetary Dynamics Test ===")
    rover_model = PlanetaryRoverDynamicsModel()
    
    night_op = rover_model.calculate_extraterrestrial_wear(ambient_temp_c=-135.0, regolith_dust_ppm=800.0)
    day_op = rover_model.calculate_extraterrestrial_wear(ambient_temp_c=15.0, regolith_dust_ppm=200.0)
    
    print("Mars Night Operation Assessment:", night_op)
    print("Mars Day Operation Assessment:", day_op)
    print("Stage 69 execution complete.")
