"""
IMS High-Frequency Acoustic Emission (AE) & Ultrasonic Signal Analysis Engine
Extracts micro-crack nucleation parameters from high-frequency acoustic signals (100 kHz - 1 MHz).
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class UltrasonicAEAnalyzer:
    """
    Processes ultrasonic Acoustic Emission (AE) signals to identify micro-structural crack initiation.
    """

    def __init__(self, sampling_rate_hz: float = 500000.0): # 500 kHz default AE rate
        self.fs = sampling_rate_hz

    def analyze_ae_signal(self, ae_signal: np.ndarray, threshold_voltage: float = 0.05) -> Dict[str, float]:
        """
        Calculates Ring-Down Counts, AE Energy, Peak Amplitude (dB AE), and AE Duration.
        """
        abs_sig = np.abs(ae_signal)
        N = len(ae_signal)

        # 1. Peak Amplitude (dB AE ref 1 uV)
        max_v = float(np.max(abs_sig))
        peak_db_ae = float(20.0 * np.log10((max_v + 1e-12) / 1e-6))

        # 2. Ring-Down Counts (threshold crossings)
        crossings = (abs_sig > threshold_voltage).astype(int)
        rd_counts = int(np.sum(np.diff(crossings) > 0))

        # 3. AE Energy (MARSE - Measured Area under Rectified Signal Envelope)
        ae_energy = float(np.sum(abs_sig**2) / self.fs)
        marse_energy = float(np.sum(abs_sig) / self.fs)

        # 4. AE Duration (microseconds)
        above_thresh_indices = np.where(abs_sig > threshold_voltage)[0]
        if len(above_thresh_indices) > 1:
            duration_us = float((above_thresh_indices[-1] - above_thresh_indices[0]) / self.fs * 1e6)
        else:
            duration_us = 0.0

        # Micro-crack indicator
        crack_risk = "HIGH" if (rd_counts > 50 or peak_db_ae > 80.0) else "NORMAL"

        return {
            "peak_amplitude_v": round(max_v, 5),
            "peak_db_ae": round(peak_db_ae, 2),
            "ring_down_counts": rd_counts,
            "ae_energy_j": round(ae_energy, 8),
            "marse_energy_vs": round(marse_energy, 6),
            "duration_us": round(duration_us, 2),
            "micro_crack_risk": crack_risk
        }

if __name__ == "__main__":
    analyzer = UltrasonicAEAnalyzer(sampling_rate_hz=500000.0)
    t = np.linspace(0, 0.002, 1000) # 2 ms sample
    
    # Healthy background noise
    healthy_ae = 0.01 * np.random.randn(1000)
    print("Healthy AE Analysis:", analyzer.analyze_ae_signal(healthy_ae))

    # Micro-crack transient burst signal
    burst_ae = 0.01 * np.random.randn(1000) + 0.3 * np.exp(-t / 0.0003) * np.sin(2 * np.pi * 150000 * t)
    print("Micro-Crack AE Burst Analysis:", analyzer.analyze_ae_signal(burst_ae))
