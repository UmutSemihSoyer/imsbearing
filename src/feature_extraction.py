import os
import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew
from scipy.fft import fft, fftfreq
from pathlib import Path
from tqdm import tqdm

from src.config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLING_RATE, SAMPLES_PER_FILE,
    BPFO, BPFI, BSF, FTF, TEST_CONFIGS
)
from src.data_loader import get_sorted_file_list, parse_file_timestamp, load_single_ims_file

def compute_time_features(signal):
    """
    Tek bir kanal zaman serisi için 11 adet istatistiksel zaman alanı özelliğini hesaplar.
    """
    abs_signal = np.abs(signal)
    mean_val = np.mean(signal)
    std_val = np.std(signal)
    rms_val = np.sqrt(np.mean(signal**2))
    peak_val = np.max(abs_signal)
    p2p_val = np.max(signal) - np.min(signal)
    kurt_val = kurtosis(signal)
    skew_val = skew(signal)
    
    mean_abs = np.mean(abs_signal)
    square_root_mean = (np.mean(np.sqrt(abs_signal)))**2
    
    crest_factor = peak_val / (rms_val + 1e-12)
    shape_factor = rms_val / (mean_abs + 1e-12)
    impulse_factor = peak_val / (mean_abs + 1e-12)
    margin_factor = peak_val / (square_root_mean + 1e-12)
    
    return {
        "mean": mean_val,
        "std": std_val,
        "rms": rms_val,
        "peak": peak_val,
        "peak_to_peak": p2p_val,
        "kurtosis": kurt_val,
        "skewness": skew_val,
        "crest_factor": crest_factor,
        "shape_factor": shape_factor,
        "impulse_factor": impulse_factor,
        "margin_factor": margin_factor,
    }

def compute_frequency_features(signal, sr=SAMPLING_RATE):
    """
    FFT spektrumu ve Rulman Karakteristik Arıza Frekanslarındaki (BPFO, BPFI, BSF, FTF)
    enerjileri hesaplar.
    """
    N = len(signal)
    yf = np.abs(fft(signal))[:N // 2]
    xf = fftfreq(N, 1 / sr)[:N // 2]
    
    # Spektral Genel Özellikler
    total_energy = np.sum(yf**2)
    mean_freq = np.sum(xf * yf) / (np.sum(yf) + 1e-12)
    
    def get_band_energy(target_freq, tolerance=5.0):
        mask = (xf >= max(0, target_freq - tolerance)) & (xf <= target_freq + tolerance)
        return np.sum(yf[mask]**2)
        
    bpfo_energy = get_band_energy(BPFO, tolerance=5.0)
    bpfi_energy = get_band_energy(BPFI, tolerance=5.0)
    bsf_energy = get_band_energy(BSF, tolerance=5.0)
    ftf_energy = get_band_energy(FTF, tolerance=2.0)
    
    return {
        "spectral_energy": total_energy,
        "spectral_mean_freq": mean_freq,
        "bpfo_energy": bpfo_energy,
        "bpfi_energy": bpfi_energy,
        "bsf_energy": bsf_energy,
        "ftf_energy": ftf_energy,
    }

def extract_features_from_test_set(test_name="test2"):
    """
    Belirtilen test seti klasöründeki tüm dosyaları tarar ve zamana göre
    özellik matrisini (DataFrame) oluşturur.
    """
    raw_dir = RAW_DATA_DIR / test_name
    if not raw_dir.exists():
        raise FileNotFoundError(f"Ham veri dizini bulunamadı: {raw_dir}")
        
    files = get_sorted_file_list(raw_dir)
    print(f"[INFO] '{test_name}' icin {len(files)} adet dosya isleniyor...")
    
    records = []
    
    for idx, file_path in enumerate(tqdm(files, desc="Ozellik Cikarimi")):
        data = load_single_ims_file(file_path)
        if data is None:
            continue
            
        timestamp = parse_file_timestamp(file_path.name)
        record = {
            "file_idx": idx,
            "filename": file_path.name,
            "timestamp": timestamp,
        }
        
        num_channels = data.shape[1]
        for ch in range(num_channels):
            channel_signal = data[:, ch]
            time_feats = compute_time_features(channel_signal)
            freq_feats = compute_frequency_features(channel_signal)
            
            for fname, val in time_feats.items():
                record[f"ch{ch+1}_{fname}"] = val
            for fname, val in freq_feats.items():
                record[f"ch{ch+1}_{fname}"] = val
                
        records.append(record)
        
    df_features = pd.DataFrame(records)
    output_csv = PROCESSED_DATA_DIR / f"features_{test_name}.csv"
    df_features.to_csv(output_csv, index=False)
    print(f"[SUCCESS] Ozellik matrisi kaydedildi: {output_csv} (Satir: {len(df_features)}, Sütun: {df_features.shape[1]})")
    return df_features

if __name__ == "__main__":
    df = extract_features_from_test_set("test2")
