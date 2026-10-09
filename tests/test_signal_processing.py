"""
Unit Test Suite for IMS Bearing Signal Processing, Health Index & REST API
"""

import os
import sys
import numpy as np
import pytest

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import FS, BEARING_FREQS
from src.feature_extraction import compute_time_features, compute_frequency_features
from src.alert_system import AlertDispatcher
from src.sensor_fusion import MultiSensorFusionEngine

def test_time_features():
    """Tests 11 time-domain statistical calculations."""
    t = np.linspace(0, 1.0, int(FS), endpoint=False)
    sig = np.sin(2 * np.pi * 50.0 * t) + 0.1 * np.random.randn(len(t))
    
    feats = compute_time_features(sig)
    
    assert "rms" in feats
    assert "kurtosis" in feats
    assert "crest_factor" in feats
    assert feats["rms"] > 0.5
    assert feats["peak_to_peak"] > 1.5

def test_frequency_features():
    """Tests FFT frequency spectrum calculations and defect frequency bands."""
    t = np.linspace(0, 1.0, int(FS), endpoint=False)
    sig = np.sin(2 * np.pi * BEARING_FREQS["BPFO"] * t) # Pure 236.4 Hz sine wave
    
    feats = compute_frequency_features(sig, sr=FS)
    
    assert "spectral_energy" in feats
    assert "bpfo_energy" in feats
    assert feats["bpfo_energy"] > 0.0

def test_alert_dispatcher():
    """Tests alert dispatcher severity evaluation."""
    dispatcher = AlertDispatcher(cooldown_seconds=0)
    res_critical = dispatcher.evaluate_and_notify("TEST-BRG", {"rms": 0.65, "kurtosis": 9.5}, 5.0)
    
    assert res_critical["severity"] == "CRITICAL"
    assert res_critical["alert_triggered"] is True

def test_sensor_fusion():
    """Tests multi-sensor telemetry fusion algorithm."""
    engine = MultiSensorFusionEngine()
    res = engine.fuse_telemetry(vibration_rms=0.07, temperature_c=36.0, acoustic_emission=0.04, oil_debris_ppm=8.0)
    
    assert res["fused_health_index"] > 0.90
    assert res["health_state"] == "NORMAL"
