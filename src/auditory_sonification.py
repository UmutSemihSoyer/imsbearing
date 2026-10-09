import numpy as np
import sys
from typing import Dict, Any

class AuditorySonifier:
    """Converts high-frequency bearing vibration into human-audible sound spectrums."""
    def __init__(self, in_sample_rate: int = 20480, target_sample_rate: int = 44100):
        self.in_sample_rate = in_sample_rate
        self.target_sample_rate = target_sample_rate

    def heterodyne_pitch_shift(self, signal: np.ndarray, shift_factor: float = 0.25) -> np.ndarray:
        """Shift ultrasonic/vibration frequencies down into 20Hz - 8kHz human hearing range."""
        # Resample or heterodyne
        t = np.arange(len(signal)) / self.in_sample_rate
        carrier = np.sin(2 * np.pi * 3000 * t)  # Modulation
        modulated = signal * carrier
        
        # Simple decimation/resampling simulation
        audible_length = int(len(signal) * shift_factor)
        audible_signal = np.interp(
            np.linspace(0, len(signal), audible_length),
            np.arange(len(signal)),
            modulated
        )
        # Normalize to [-1.0, 1.0]
        max_val = np.max(np.abs(audible_signal))
        if max_val > 0:
            audible_signal = audible_signal / max_val
        return audible_signal

    def compute_musical_pitch_degradation(self, rms: float, kurtosis: float) -> Dict[str, Any]:
        """Maps bearing degradation metrics to musical pitch (Hz) and timbre distortion."""
        base_pitch = 440.0  # Note A4 (Healthy)
        pitch_shift = (rms * 50.0) + (max(0, kurtosis - 3.0) * 20.0)
        current_pitch = base_pitch + pitch_shift
        
        # Determine audio mood/dissonance
        if current_pitch < 480:
            timbre = "Harmonic Pure Tone (Healthy)"
            urgency = "LOW"
        elif current_pitch < 600:
            timbre = "Metallic Humming (Early Flaking)"
            urgency = "MEDIUM"
        else:
            timbre = "Harsh Dissonant Grating (Critical Spalling)"
            urgency = "HIGH"

        return {
            "base_frequency_hz": round(current_pitch, 2),
            "timbre_description": timbre,
            "dissonance_score": float(np.clip((kurtosis - 3.0) / 10.0, 0.0, 1.0)),
            "urgency": urgency
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Stage 62: Auditory Sonification Test ===")
    sonifier = AuditorySonifier(in_sample_rate=20480)
    
    # Healthy signal vs Severe Spall signal
    healthy_sig = np.random.normal(0, 0.05, 4096)
    faulty_sig = np.random.normal(0, 0.8, 4096) + np.sin(2 * np.pi * 120 * np.arange(4096)/20480) * 1.5
    
    audible = sonifier.heterodyne_pitch_shift(faulty_sig)
    print(f"Generated audible audio stream: {len(audible)} audio samples.")
    
    healthy_audio = sonifier.compute_musical_pitch_degradation(rms=0.05, kurtosis=2.9)
    faulty_audio = sonifier.compute_musical_pitch_degradation(rms=1.25, kurtosis=12.4)
    
    print("Healthy Audio Pitch Profile:", healthy_audio)
    print("Faulty Audio Pitch Profile:", faulty_audio)
    print("Stage 62 execution complete.")
