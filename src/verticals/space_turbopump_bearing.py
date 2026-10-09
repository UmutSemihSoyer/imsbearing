import numpy as np
import sys
from typing import Dict, Any

class SpaceTurbopumpBearingAnalyzer:
    """Ek G: Space Probes & Rocket Turbopumps Vertical Adaptation."""
    
    def analyze_rocket_turbopump(
        self,
        raw_signal: np.ndarray,
        turbopump_rpm: float = 120000.0,
        cosmic_ray_spikes_detected: int = 12
    ) -> Dict[str, Any]:
        """
        G.1: Liquid oxygen/hydrogen turbopump 100,000+ RPM cavitation & bearing wear.
        G.2: Cosmic ray radiation spike rejection filter.
        """
        # Remove single-sample cosmic ray radiation spikes (despiking filter)
        median_filtered = np.copy(raw_signal)
        std_dev = np.std(raw_signal)
        median_val = np.median(raw_signal)
        
        # Despiking mask
        spike_mask = np.abs(raw_signal - median_val) > 4.0 * std_dev
        median_filtered[spike_mask] = median_val
        
        cleaned_rms = float(np.sqrt(np.mean(median_filtered ** 2)))
        
        # Cavitation risk index
        cavitation_score = min(1.0, (turbopump_rpm / 150000.0) * (cleaned_rms / 0.5))

        return {
            "vertical_domain": "ROCKET_TURBOPUMP_SPACE_PROPULSION",
            "turbopump_rpm": turbopump_rpm,
            "cosmic_ray_spikes_filtered": int(np.sum(spike_mask)),
            "cleaned_signal_rms_g": round(cleaned_rms, 4),
            "cryogenic_cavitation_risk_score": round(cavitation_score, 3),
            "turbopump_health": "OPTIMAL_BURST_RATED" if cavitation_score < 0.7 else "CAVITATION_INDUCED_VIBRATION"
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Appendix G: Rocket Turbopump Test ===")
    analyzer = SpaceTurbopumpBearingAnalyzer()
    sig = np.random.normal(0, 0.2, 2048)
    sig[100] = 50.0  # Cosmic ray spike!
    res = analyzer.analyze_rocket_turbopump(sig)
    print("Rocket Turbopump Output:", res)
    print("Appendix G execution complete.")
