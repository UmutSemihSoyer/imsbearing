import numpy as np
import sys
from typing import Dict, Any

class PiezoelectricEnergyHarvester:
    """Calculates kinetic energy harvested from bearing vibration via PZT transducers."""
    def __init__(self, pzt_coupling_coefficient: float = 0.35, transducer_area_cm2: float = 5.0):
        self.coupling_coeff = pzt_coupling_coefficient
        self.area_m2 = transducer_area_cm2 * 1e-4

    def calculate_harvested_power(self, acceleration_g_rms: float, dominant_freq_hz: float) -> Dict[str, Any]:
        """
        P = 0.5 * d33 * A * (a_rms * g)^2 * f
        Calculates instantaneous power (mW), energy per hour (mWh), and battery self-sufficiency status.
        """
        g_to_ms2 = 9.81
        a_ms2 = acceleration_g_rms * g_to_ms2
        
        # Piezoelectric power output formulation
        power_watts = 0.5 * self.coupling_coeff * self.area_m2 * (a_ms2 ** 2) * dominant_freq_hz * 1e-3
        power_mw = power_watts * 1000.0
        energy_mwh_per_hour = power_mw * 1.0
        
        # Sensor power consumption benchmark (e.g. BLE transmission = 0.5 mW avg)
        ble_sensor_power_mw = 0.5
        is_self_powered = power_mw >= ble_sensor_power_mw

        return {
            "acceleration_g_rms": round(acceleration_g_rms, 3),
            "vibration_frequency_hz": round(dominant_freq_hz, 1),
            "generated_power_mw": round(power_mw, 4),
            "energy_harvested_mwh_day": round(energy_mwh_per_hour * 24.0, 3),
            "ble_sensor_demand_mw": ble_sensor_power_mw,
            "is_100pct_self_powered": is_self_powered,
            "battery_life_extension_pct": round(min(100.0, (power_mw / ble_sensor_power_mw) * 100.0), 1)
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Stage 63: Piezoelectric Energy Harvesting Test ===")
    harvester = PiezoelectricEnergyHarvester()
    
    low_vib = harvester.calculate_harvested_power(acceleration_g_rms=0.15, dominant_freq_hz=120.0)
    high_vib = harvester.calculate_harvested_power(acceleration_g_rms=0.85, dominant_freq_hz=240.0)
    
    print("Low Vibration Harvesting Output:", low_vib)
    print("High Vibration Harvesting Output:", high_vib)
    print("Stage 63 execution complete.")
