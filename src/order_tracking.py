"""
IMS Order Tracking & Angle Domain Resampling Module
Normalizes vibration signals under variable motor RPM by resampling from time-domain to shaft angle domain.
"""

import os
import sys
import numpy as np
from scipy.interpolate import interp1d
from scipy.fft import fft, fftfreq
from typing import Dict, Any, Tuple

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import FS, BEARING_FREQS

class OrderTrackingAnalyzer:
    """
    Performs Order Tracking by resampling non-stationary time signals into equal angular increments.
    """

    def __init__(self, n_pulses_per_rev: int = 1):
        self.ppr = n_pulses_per_rev

    def resample_to_angle_domain(self, signal: np.ndarray, rpm_profile: np.ndarray, fs: float = FS) -> Tuple[np.ndarray, np.ndarray]:
        """
        Resamples time-domain vibration signal into constant angle increments (radians).
        """
        N = len(signal)
        t = np.linspace(0, N / fs, N, endpoint=False)

        # Convert RPM to instantaneous Shaft Angular Velocity (rad/s)
        omega_t = (rpm_profile / 60.0) * (2.0 * np.pi)

        # Cumulative shaft rotation angle theta(t) (radians)
        theta_t = np.cumsum(omega_t) * (1.0 / fs)

        # Uniform angle grid (e.g. 1024 points per revolution)
        total_revolutions = theta_t[-1] / (2.0 * np.pi)
        n_angle_samples = int(total_revolutions * 512)
        theta_uniform = np.linspace(0, theta_t[-1], n_angle_samples, endpoint=False)

        # Interpolate vibration signal onto uniform angle grid
        interpolator = interp1d(theta_t, signal, kind="cubic", fill_value="extrapolate")
        signal_angle_domain = interpolator(theta_uniform)

        return theta_uniform, signal_angle_domain

    def compute_order_spectrum(self, signal_angle_domain: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes Order Spectrum (Amplitude vs Orders [Order = Freq / Shaft_Speed]).
        """
        N = len(signal_angle_domain)
        order_fft = np.abs(fft(signal_angle_domain))[:N // 2] * (2.0 / N)
        orders = np.linspace(0, 256, N // 2, endpoint=False)

        return orders, order_fft

if __name__ == "__main__":
    analyzer = OrderTrackingAnalyzer()
    
    # Simulate variable speed acceleration (1500 RPM -> 3000 RPM)
    N = 20000
    t = np.linspace(0, 1.0, N)
    rpm_t = np.linspace(1500, 3000, N) # Ramping RPM
    
    # Outer Race Fault order = 236.4 Hz / (2000 RPM / 60) = 7.092 Orders
    shaft_freq_t = rpm_t / 60.0
    sig_var = np.sin(2 * np.pi * (7.092 * shaft_freq_t) * t) + 0.1 * np.random.randn(N)

    theta_grid, sig_angle = analyzer.resample_to_angle_domain(sig_var, rpm_t)
    orders, order_amps = analyzer.compute_order_spectrum(sig_angle)

    print(f"[SUCCESS] Order Tracking completed: Resampled to {len(sig_angle)} angle samples.")
    print(f"[STATS] Peak Order detected: {orders[np.argmax(order_amps[1:])+1]:.3f} Orders (Expected: 7.092 BPFO Order)")
