"""
IMS Bearing Real-Time IoT Streaming Simulator
Simulates live industrial vibration sensor stream from bearing snapshots or synthetic degradation signals.
Broadcasts telemetry packets to REST API endpoints or local streaming subscribers.
"""

import time
import argparse
import sys
import os
import json
import numpy as np
import requests

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import FS, BEARING_FREQS, DEGRADATION_THRESHOLDS
from src.feature_extraction import compute_time_features, compute_frequency_features


class IoTBearingSensorSimulator:
    """
    Simulates a 4-channel accelerometer installed on a Rexnord ZA-2115 bearing assembly.
    Generates realistic 20 kHz vibration data with progressively increasing outer race (BPFO) defect energy.
    """

    def __init__(self, sampling_rate: int = FS, duration_sec: float = 1.0, total_steps: int = 100):
        self.fs = sampling_rate
        self.duration = duration_sec
        self.total_steps = total_steps
        self.current_step = 0

    def generate_snapshot(self, step: int) -> np.ndarray:
        """Generates 1-second 20 kHz vibration snapshot with simulated degradation."""
        t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
        degradation_factor = (step / max(1, self.total_steps - 1)) ** 3
        
        # Base healthy signal: random normal noise + 100 Hz shaft rotation frequency
        shaft_freq = 30.0  # 1800 RPM = 30 Hz
        signal = 0.05 * np.random.randn(len(t)) + 0.02 * np.sin(2 * np.pi * shaft_freq * t)

        # Fault impact component (BPFO = 236.4 Hz)
        if degradation_factor > 0.1:
            bpfo_freq = BEARING_FREQS["BPFO"]
            impact_signal = np.sin(2 * np.pi * bpfo_freq * t) * (1.0 + 0.5 * np.sin(2 * np.pi * shaft_freq * t))
            # Exponential impulse train simulation
            spikes = (np.sin(2 * np.pi * bpfo_freq * t) > 0.98).astype(float) * 2.0
            signal += degradation_factor * (impact_signal + spikes)

        return signal

    def stream_packet(self, step: int) -> dict:
        """Extracts features from the generated signal and constructs an IoT JSON telemetry packet."""
        signal = self.generate_snapshot(step)
        
        time_feats = compute_time_features(signal)
        fft_feats = compute_frequency_features(signal, self.fs)


        packet = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "step": step,
            "sensor_id": "VIB-BRG-01-ACCEL",
            "features": {
                "rms": round(float(time_feats["rms"]), 5),
                "kurtosis": round(float(time_feats["kurtosis"]), 4),
                "skewness": round(float(time_feats["skewness"]), 4),
                "peak_to_peak": round(float(time_feats["peak_to_peak"]), 4),
                "crest_factor": round(float(time_feats["crest_factor"]), 4),
                "shape_factor": round(float(time_feats["shape_factor"]), 4),
                "impulse_factor": round(float(time_feats["impulse_factor"]), 4),
                "margin_factor": round(float(time_feats["margin_factor"]), 4),
                "spectral_energy": round(float(fft_feats["spectral_energy"]), 6),
                "bpfo_energy": round(float(fft_feats["bpfo_energy"]), 6),
                "bpfi_energy": round(float(fft_feats["bpfi_energy"]), 6)
            }
        }
        return packet, signal

def run_simulation(api_url: str = "http://localhost:8000/api/v1/predict_rul", interval: float = 0.5, total_steps: int = 50, post_to_api: bool = False):
    """Runs the live streaming loop, printing telemetry data and optionally sending POST requests to the API."""
    simulator = IoTBearingSensorSimulator(total_steps=total_steps)

    print(f"[INFO] Starting IoT Sensor Simulator...")
    print(f"[INFO] Streaming target: {api_url if post_to_api else 'Local Console'}")
    print(f"[INFO] Update interval: {interval} seconds | Total steps: {total_steps}\n")
    print("-" * 80)
    print(f"{'Step':<6} | {'RMS':<8} | {'Kurtosis':<8} | {'Pred RUL (h)':<14} | {'Health Status':<25} | {'Source'}")
    print("-" * 80)

    for step in range(total_steps):
        packet, raw_signal = simulator.stream_packet(step)
        feats = packet["features"]

        status_str = "Healthy"
        predicted_rul = 160.0 * (1.0 - step / total_steps)

        if post_to_api:
            try:
                resp = requests.post(api_url, json={"features": feats, "model_type": "random_forest"}, timeout=2.0)
                if resp.status_code == 200:
                    data = resp.json()
                    predicted_rul = data["predicted_rul_hours"]
                    status_str = data["status"]
            except Exception as e:
                status_str = f"API Offline (Fallback: RUL={predicted_rul:.1f}h)"

        else:
            if feats["kurtosis"] > DEGRADATION_THRESHOLDS["kurtosis_critical"] or feats["rms"] > DEGRADATION_THRESHOLDS["rms_critical"]:
                status_str = "CRITICAL - Severe Damage"
            elif feats["kurtosis"] > DEGRADATION_THRESHOLDS["kurtosis_warning"] or feats["rms"] > DEGRADATION_THRESHOLDS["rms_warning"]:
                status_str = "WARNING - Early Wearing"

        print(f"{step:<6} | {feats['rms']:<8.4f} | {feats['kurtosis']:<8.2f} | {predicted_rul:<14.1f} | {status_str:<25} | IoT Packet")
        time.sleep(interval)

    print("-" * 80)
    print("[SUCCESS] Streaming simulation completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IMS Bearing IoT Live Streaming Simulator")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000/api/v1/predict_rul", help="Target REST API URL")
    parser.add_argument("--interval", type=float, default=0.2, help="Streaming interval in seconds")
    parser.add_argument("--steps", type=int, default=30, help="Total simulation steps")
    parser.add_argument("--post-api", action="store_true", help="Send live POST requests to FastAPI server")

    args = parser.parse_args()
    run_simulation(api_url=args.api_url, interval=args.interval, total_steps=args.steps, post_to_api=args.post_api)
