"""
IMS Bearing Predictive Maintenance & RUL Estimation API
FastAPI service exposing REST endpoints for RUL prediction, health assessment, and FFT signal analysis.
"""

from typing import List, Optional, Dict, Any
import os
import sys
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import FS, BEARING_FREQS, DEGRADATION_THRESHOLDS

app = FastAPI(
    title="IMS Bearing Predictive Maintenance API",
    description="RESTful API for real-time vibration analysis, bearing health index estimation, RUL prediction, and FFT fault diagnosis.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend/dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for cached model artifacts
MODEL_CACHE = {}

def get_loaded_models():
    """Load and cache trained ML models if available."""
    if "rf_model" not in MODEL_CACHE:
        model_path = os.path.join("models", "rf_rul_model_test2.joblib")
        scaler_path = os.path.join("models", "scaler_test2.joblib")
        iso_path = os.path.join("models", "iso_forest_test2.joblib")
        
        if os.path.exists(model_path):
            try:
                MODEL_CACHE["rf_model"] = joblib.load(model_path)
            except Exception:
                MODEL_CACHE["rf_model"] = None
        else:
            MODEL_CACHE["rf_model"] = None

        if os.path.exists(scaler_path):
            try:
                MODEL_CACHE["scaler"] = joblib.load(scaler_path)
            except Exception:
                MODEL_CACHE["scaler"] = None
        else:
            MODEL_CACHE["scaler"] = None

        if os.path.exists(iso_path):
            try:
                MODEL_CACHE["iso_forest"] = joblib.load(iso_path)
            except Exception:
                MODEL_CACHE["iso_forest"] = None
        else:
            MODEL_CACHE["iso_forest"] = None

    return MODEL_CACHE

# Pydantic Schemas
class FeatureVector(BaseModel):
    rms: float = Field(..., example=0.125, description="Root Mean Square value")
    kurtosis: float = Field(..., example=3.42, description="Kurtosis value")
    skewness: float = Field(0.0, example=0.15, description="Skewness value")
    peak_to_peak: float = Field(..., example=0.85, description="Peak-to-Peak amplitude")
    crest_factor: float = Field(..., example=3.80, description="Crest factor")
    shape_factor: float = Field(1.25, example=1.22, description="Shape factor")
    impulse_factor: float = Field(4.5, example=4.2, description="Impulse factor")
    margin_factor: float = Field(5.0, example=5.1, description="Margin factor")
    spectral_energy: float = Field(..., example=0.015, description="FFT Total Spectral Energy")
    bpfo_energy: float = Field(0.002, example=0.005, description="BPFO fault band energy")
    bpfi_energy: float = Field(0.001, example=0.002, description="BPFI fault band energy")

class RULPredictionRequest(BaseModel):
    features: FeatureVector
    model_type: Optional[str] = Field("random_forest", example="random_forest", description="Model to use: random_forest, iso_forest, baseline")

class RULPredictionResponse(BaseModel):
    predicted_rul_hours: float
    health_index: float
    status: str
    anomaly_flag: bool
    model_used: str

class HealthStatusRequest(BaseModel):
    health_index: float = Field(..., ge=0.0, le=1.0, example=0.75, description="Calculated HI (0.0=Failed, 1.0=Healthy)")

class HealthStatusResponse(BaseModel):
    health_index: float
    degradation_stage: str
    severity_level: str
    recommended_action: str

class FFTAnalysisRequest(BaseModel):
    signal: List[float] = Field(..., description="Vibration time-series data array")
    sampling_rate: Optional[float] = Field(20000.0, description="Sampling rate in Hz")

class FFTAnalysisResponse(BaseModel):
    sampling_rate: float
    dominant_frequency_hz: float
    spectral_energy: float
    spectral_centroid_hz: float
    bpfo_amplitude: float
    bpfi_amplitude: float
    bsf_amplitude: float
    ftf_amplitude: float
    top_frequencies_hz: List[float]
    top_amplitudes: List[float]

# API Endpoints
@app.get("/")
def read_root():
    """Root endpoint for API service health check."""
    return {
        "status": "online",
        "service": "IMS Bearing Predictive Maintenance API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/v1/health")
def health_check():
    """Returns operational status of API and loaded models."""
    models = get_loaded_models()
    return {
        "status": "healthy",
        "models_loaded": {
            "random_forest": models.get("rf_model") is not None,
            "scaler": models.get("scaler") is not None,
            "isolation_forest": models.get("iso_forest") is not None
        },
        "bearing_parameters": BEARING_FREQS
    }

@app.post("/api/v1/predict_rul", response_model=RULPredictionResponse)
def predict_rul(request: RULPredictionRequest):
    """Predict Remaining Useful Life (RUL) and Health Index based on input signal features."""
    feat = request.features
    models = get_loaded_models()
    rf_model = models.get("rf_model")
    scaler = models.get("scaler")
    iso_forest = models.get("iso_forest")

    # Feature array matching feature_extraction schema (11 features)
    feature_vals = np.array([[
        feat.rms, feat.kurtosis, feat.skewness, feat.peak_to_peak,
        feat.crest_factor, feat.shape_factor, feat.impulse_factor,
        feat.margin_factor, feat.spectral_energy, feat.bpfo_energy, feat.bpfi_energy
    ]])

    predicted_rul = 50.0  # Fallback RUL (hours)
    health_idx = 1.0
    model_used = request.model_type

    if rf_model is not None and scaler is not None:
        try:
            scaled_vals = scaler.transform(feature_vals)
            predicted_rul = float(rf_model.predict(scaled_vals)[0])
            model_used = "RandomForestRegressor"
        except Exception:
            # Physics-based baseline fallback calculation
            predicted_rul = float(np.clip(100.0 - (feat.rms * 200.0 + feat.kurtosis * 5.0), 0.0, 160.0))
            model_used = "RuleBasedFallback"
    else:
        # Rule-based fallback if model not loaded
        predicted_rul = float(np.clip(160.0 * (1.0 - np.minimum(1.0, feat.rms / 0.5)), 0.0, 160.0))
        model_used = "RuleBasedFallback"

    # Compute Health Index (1.0 healthy -> 0.0 failed)
    health_idx = float(np.clip(predicted_rul / 160.0, 0.0, 1.0))

    # Anomaly detection check
    anomaly_flag = False
    if iso_forest is not None and scaler is not None:
        try:
            scaled_vals = scaler.transform(feature_vals)
            pred = iso_forest.predict(scaled_vals)[0]
            anomaly_flag = bool(pred == -1)
        except Exception:
            anomaly_flag = bool(feat.kurtosis > DEGRADATION_THRESHOLDS["kurtosis_warning"] or feat.rms > DEGRADATION_THRESHOLDS["rms_warning"])
    else:
        anomaly_flag = bool(feat.kurtosis > DEGRADATION_THRESHOLDS["kurtosis_warning"] or feat.rms > DEGRADATION_THRESHOLDS["rms_warning"])

    if health_idx > 0.7:
        status = "Healthy"
    elif health_idx > 0.3:
        status = "Warning - Degradation Detected"
    else:
        status = "Critical - Immediate Maintenance Required"

    return RULPredictionResponse(
        predicted_rul_hours=round(predicted_rul, 2),
        health_index=round(health_idx, 4),
        status=status,
        anomaly_flag=anomaly_flag,
        model_used=model_used
    )

@app.post("/api/v1/health_status", response_model=HealthStatusResponse)
def get_health_status(request: HealthStatusRequest):
    """Categorizes health status and provides prescriptive maintenance advice."""
    hi = request.health_index

    if hi >= 0.8:
        stage = "Stage 1: Normal Operation"
        severity = "Low (Normal)"
        action = "Continuous online monitoring. Standard maintenance schedule."
    elif hi >= 0.5:
        stage = "Stage 2: Early Degradation"
        severity = "Moderate (Warning)"
        action = "Increase vibration monitoring frequency. Order spare Rexnord ZA-2115 bearing."
    elif hi >= 0.2:
        stage = "Stage 3: Advanced Degradation"
        severity = "High (Severe)"
        action = "Schedule maintenance window within 24 hours. Prepare lubrication and replacement tools."
    else:
        stage = "Stage 4: Imminent Failure"
        severity = "Critical (Danger)"
        action = "STOP MACHINE IMMEDIATELY. Perform emergency bearing replacement to avoid catastrophic housing damage."

    return HealthStatusResponse(
        health_index=round(hi, 4),
        degradation_stage=stage,
        severity_level=severity,
        recommended_action=action
    )

@app.post("/api/v1/fft_analysis", response_model=FFTAnalysisResponse)
def analyze_fft(request: FFTAnalysisRequest):
    """Computes FFT frequency spectrum, spectral centroid, and matches characteristic fault frequencies."""
    sig = np.array(request.signal, dtype=np.float64)
    fs = request.sampling_rate

    if len(sig) < 16:
        raise HTTPException(status_code=400, detail="Signal vector must contain at least 16 data points.")

    N = len(sig)
    # FFT calculation
    fft_vals = np.abs(np.fft.rfft(sig)) * (2.0 / N)
    freqs = np.fft.rfftfreq(N, 1.0 / fs)

    # Spectral Energy & Centroid
    spectral_energy = float(np.sum(fft_vals ** 2))
    spectral_centroid = float(np.sum(freqs * fft_vals) / (np.sum(fft_vals) + 1e-12))

    # Find dominant frequency
    max_idx = np.argmax(fft_vals[1:]) + 1  # ignore DC component
    dominant_freq = float(freqs[max_idx])

    # Function to extract energy around characteristic frequency
    def get_band_amp(target_freq, df=5.0):
        mask = (freqs >= (target_freq - df)) & (freqs <= (target_freq + df))
        return float(np.max(fft_vals[mask])) if np.any(mask) else 0.0

    bpfo_amp = get_band_amp(BEARING_FREQS["BPFO"])
    bpfi_amp = get_band_amp(BEARING_FREQS["BPFI"])
    bsf_amp = get_band_amp(BEARING_FREQS["BSF"])
    ftf_amp = get_band_amp(BEARING_FREQS["FTF"])

    # Top 5 frequencies
    top_indices = np.argsort(fft_vals)[::-1][:5]
    top_freqs = freqs[top_indices].tolist()
    top_amps = fft_vals[top_indices].tolist()

    return FFTAnalysisResponse(
        sampling_rate=fs,
        dominant_frequency_hz=round(dominant_freq, 2),
        spectral_energy=round(spectral_energy, 6),
        spectral_centroid_hz=round(spectral_centroid, 2),
        bpfo_amplitude=round(bpfo_amp, 6),
        bpfi_amplitude=round(bpfi_amp, 6),
        bsf_amplitude=round(bsf_amp, 6),
        ftf_amplitude=round(ftf_amp, 6),
        top_frequencies_hz=[round(f, 2) for f in top_freqs],
        top_amplitudes=[round(a, 6) for a in top_amps]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
