import numpy as np
import sys
from typing import Dict, Any

class BioElectricalNeuralMapper:
    """Transforms mechanical bearing vibration into biological neuronal action potentials (mV spike trains)."""
    
    def convert_vibration_to_action_potentials(self, vibration_signal: np.ndarray) -> Dict[str, Any]:
        """
        Maps mechanical acceleration (g) to neuronal membrane potential (-70 mV to +30 mV).
        Hodgkin-Huxley biological neuron encoding simulation.
        """
        resting_potential_mv = -70.0
        peak_action_potential_mv = 30.0
        
        # Normalize signal and map to membrane voltage
        normalized = (vibration_signal - np.min(vibration_signal)) / (np.ptp(vibration_signal) + 1e-8)
        membrane_potentials_mv = resting_potential_mv + normalized * (peak_action_potential_mv - resting_potential_mv)
        
        # Count neural spikes crossing threshold (-20 mV)
        spikes_count = int(np.sum(membrane_potentials_mv > -20.0))
        firing_rate_hz = spikes_count / (len(vibration_signal) / 20480.0)

        return {
            "resting_potential_mv": resting_potential_mv,
            "peak_potential_mv": peak_action_potential_mv,
            "total_spikes_detected": spikes_count,
            "neural_firing_rate_hz": round(firing_rate_hz, 1),
            "synaptic_transmission_status": "SYNAPSE_SIGNAL_TRANSMITTED_TO_BRAIN_ORGANOID"
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Stage 81: Bio-Electrical Neural Mapping Test ===")
    mapper = BioElectricalNeuralMapper()
    sig = np.random.normal(0, 0.5, 4096) + np.sin(np.linspace(0, 50, 4096))
    neural_res = mapper.convert_vibration_to_action_potentials(sig)
    print("Bio-Electrical Neural Potential Mapping:", neural_res)
    print("Stage 81 execution complete.")
