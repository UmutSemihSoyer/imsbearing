"""
IMS Peer-to-Peer Bearing Benchmarking Engine
Compares degradation trajectories of twin sister bearings operating under identical shaft speeds & loads.
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class PeerBearingBenchmarker:
    """
    Benchmarks wear rates across sister bearings installed on identical machine assemblies.
    """

    def benchmark_sister_bearings(self, bearing_a_rms: np.ndarray, bearing_b_rms: np.ndarray,
                                  bearing_a_id: str = "Bearing-1 (DE)",
                                  bearing_b_id: str = "Bearing-2 (NDE)") -> Dict[str, Any]:
        """
        Calculates wear rate ratio and detects abnormal premature degradation.
        """
        # Linear slope of RMS degradation over time
        x = np.arange(len(bearing_a_rms))
        slope_a = float(np.polyfit(x, bearing_a_rms, 1)[0])
        slope_b = float(np.polyfit(x, bearing_b_rms, 1)[0])

        wear_ratio = float(slope_a / (slope_b + 1e-8))

        if wear_ratio > 2.0:
            anomaly_assessment = f"{bearing_a_id} is degrading {wear_ratio:.1f}x faster than twin {bearing_b_id} (Severe Premature Wear)"
        elif wear_ratio < 0.5:
            anomaly_assessment = f"{bearing_b_id} is degrading {1.0/wear_ratio:.1f}x faster than twin {bearing_a_id} (Severe Premature Wear)"
        else:
            anomaly_assessment = "Sister bearings exhibiting symmetrical uniform wear rate."

        return {
            "bearing_a_id": bearing_a_id,
            "bearing_b_id": bearing_b_id,
            "bearing_a_wear_slope": round(slope_a, 6),
            "bearing_b_wear_slope": round(slope_b, 6),
            "wear_rate_ratio": round(wear_ratio, 3),
            "benchmark_result": anomaly_assessment
        }

if __name__ == "__main__":
    benchmarker = PeerBearingBenchmarker()
    
    # Simulate twin bearings: Bearing 1 degrading rapidly, Bearing 2 staying healthy
    rms_a = np.linspace(0.08, 0.65, 50) # Rapid wear
    rms_b = np.linspace(0.08, 0.12, 50) # Normal wear

    res = benchmarker.benchmark_sister_bearings(rms_a, rms_b)
    print("Peer-to-Peer Benchmark Analysis:", res)
