"""
IMS Sensor Data Validation & Cyber-Security Integrity Filter
Detects cable disconnection, parasitic EM noise spikes, signal clipping, and sensor tampering attempts.
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class SensorDataIntegrityFilter:
    """
    Validates sensor telemetry integrity before sending to ML models.
    """

    def validate_signal_integrity(self, signal: np.ndarray, max_voltage_range: float = 10.0) -> Dict[str, Any]:
        """
        Runs 4 cyber-security & hardware validation checks on raw vibration signal.
        """
        std_val = float(np.std(signal))
        peak_val = float(np.max(np.abs(signal)))
        mean_val = float(np.mean(signal))

        is_valid = True
        fault_type = "NONE"

        # Check 1: Cable Disconnection / Open Circuit (Flatline)
        if std_val < 1e-5:
            is_valid = False
            fault_type = "CABLE_DISCONNECTED_FLATLINE"

        # Check 2: Signal Clipping / Saturation
        elif np.sum(np.abs(signal) >= (max_voltage_range * 0.98)) > (0.02 * len(signal)):
            is_valid = False
            fault_type = "SENSOR_SATURATION_CLIPPING"

        # Check 3: Parasitic Electromagnetic Spike / ESD Impulse
        elif peak_val > (15.0 * (std_val + 1e-6)):
            is_valid = False
            fault_type = "PARASITIC_EM_NOISE_SPIKE"

        # Check 4: DC Offset Drift (Sensor mounting loose)
        elif abs(mean_val) > 2.5:
            is_valid = False
            fault_type = "DC_OFFSET_DRIFT_LOOSE_MOUNT"

        return {
            "is_valid": is_valid,
            "integrity_fault": fault_type,
            "signal_std": round(std_val, 5),
            "signal_peak": round(peak_val, 4),
            "signal_dc_mean": round(mean_val, 4),
            "action": "PASS TO ML PIPELINE" if is_valid else f"REJECT SIGNAL ({fault_type})"
        }

if __name__ == "__main__":
    validator = SensorDataIntegrityFilter()
    
    # Valid Healthy Signal
    valid_sig = 0.05 * np.random.randn(2048)
    print("Healthy Signal Check:", validator.validate_signal_integrity(valid_sig))

    # Flatline Disconnected Cable
    flat_sig = np.zeros(2048)
    print("Flatline Check:", validator.validate_signal_integrity(flat_sig))

    # Parasitic Noise Spike
    spike_sig = 0.05 * np.random.randn(2048)
    spike_sig[500] = 9.8 # Parasitic spike
    print("Spike Check:", validator.validate_signal_integrity(spike_sig))
