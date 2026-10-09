import numpy as np
import pandas as pd
from scipy.signal import hilbert, butter, filtfilt
from scipy.stats import kurtosis
from scipy.fft import fft, fftfreq
from pathlib import Path

from src.config import SAMPLING_RATE, BPFO, BPFI, BSF, FTF, PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.data_loader import get_sorted_file_list, load_single_ims_file

def bandpass_filter(signal, lowcut, highcut, fs=SAMPLING_RATE, order=4):
    """
    Belirli frekans aralığını süzmek için Butterworth Band-pass Filtresi uygular.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, signal)
    return y

def wavelet_denoise(signal, threshold_factor=0.04):
    """
    8.2. Wavelet Denoising (Dalgacık Gürültü Giderme):
    Sinyaldeki yüksek frekanslı beyaz gürültüyü süzmek için Dalgacık Yumuşak Eşikleme (Soft Thresholding) uygular.
    """
    try:
        import pywt
        wavelet = 'sym4'
        level = 4
        coeffs = pywt.wavedec(signal, wavelet, level=level)
        # Donoho & Johnstone Evrensel Eşik (Universal Threshold)
        sigma = (1 / 0.6745) * np.median(np.abs(coeffs[-1] - np.median(coeffs[-1])))
        threshold = sigma * np.sqrt(2 * np.log(len(signal))) * threshold_factor
        
        new_coeffs = [coeffs[0]]
        for c in coeffs[1:]:
            new_coeffs.append(pywt.threshold(c, threshold, mode='soft'))
            
        denoised_signal = pywt.waverec(new_coeffs, wavelet)
        return denoised_signal[:len(signal)]
    except ImportError:
        # PyWavelets yoksa frekans etki alanında FFT yumuşatması fallback
        N = len(signal)
        yf = fft(signal)
        cutoff = int(N * 0.35)
        yf[cutoff:N-cutoff] *= 0.1
        return np.real(np.fft.ifft(yf))

def compute_emd_imfs(signal, max_imfs=4):
    """
    8.4. EMD (Empirical Mode Decomposition):
    Ham titreşim sinyalini Intrinsic Mode Functions (IMF) bileşenlerine ayırır.
    """
    imfs = []
    residual = signal.copy()
    
    for _ in range(max_imfs):
        # Basitleştirilmiş sifting süreci
        h = residual.copy()
        for _ in range(3):
            # Yerel ekstremum noktalarını yumuşatma
            mean_env = (bandpass_filter(h, 50, 4000) + h) / 2.0
            h = h - mean_env
        imfs.append(h)
        residual = residual - h
        
    # IMF Enerjileri
    imf_energies = [np.sum(imf**2) for imf in imfs]
    return imfs, imf_energies

def compute_envelope_spectrum(signal, lowcut=1000, highcut=4000, fs=SAMPLING_RATE):
    """
    8.1. Hilbert Dönüşümü kullanarak Zarf Spektrumu (Envelope Spectrum) hesaplar.
    Dış ve iç bilezik darbe tekrarlama frekanslarını (BPFO/BPFI) netleştirir.
    """
    # Öncesinde gürültü temizleme
    clean_signal = wavelet_denoise(signal)
    
    # Bandpass Filtreleme
    filtered_sig = bandpass_filter(clean_signal, lowcut=lowcut, highcut=highcut, fs=fs)
    
    # Hilbert Dönüşümü ile Analitik Sinyal ve Zarf (Envelope)
    analytic_signal = hilbert(filtered_sig)
    envelope = np.abs(analytic_signal)
    
    envelope_detrend = envelope - np.mean(envelope)
    
    N = len(envelope_detrend)
    env_fft = np.abs(fft(envelope_detrend))[:N // 2]
    freqs = fftfreq(N, 1 / fs)[:N // 2]
    
    return freqs, env_fft, envelope

def compute_fast_kurtogram(signal, max_level=4, fs=SAMPLING_RATE):
    """
    8.3. Sinyalin basıklığının (Kurtosis) en yüksek olduğu optimal frekans bandını ve
    bant genişliğini bulan Fast Kurtogram analitiği.
    """
    best_kurtosis = -1
    best_band = (1000, 4000)
    
    nyquist = fs / 2.0
    for level in range(1, max_level + 1):
        num_bands = 2**level
        bandwidth = nyquist / num_bands
        for b_idx in range(num_bands):
            lowcut = max(50, b_idx * bandwidth)
            highcut = min(nyquist - 50, (b_idx + 1) * bandwidth)
            
            if highcut - lowcut < 200:
                continue
                
            try:
                filt_sig = bandpass_filter(signal, lowcut, highcut, fs=fs)
                env = np.abs(hilbert(filt_sig))
                k = kurtosis(env)
                
                if k > best_kurtosis:
                    best_kurtosis = k
                    best_band = (lowcut, highcut)
            except Exception:
                continue
                
    return best_band, best_kurtosis

def extract_advanced_envelope_features(test_name="test2"):
    """
    Tüm test setindeki verilere Wavelet Denoising, EMD ve Zarf Analizi uygular
    ve sonuçları kaydeder.
    """
    raw_dir = RAW_DATA_DIR / test_name
    if not raw_dir.exists():
        raise FileNotFoundError(f"Ham veri klasörü bulunamadı: {raw_dir}")
        
    files = get_sorted_file_list(raw_dir)
    print(f"[INFO] Gelismis Sinyal Islemi (Wavelet + EMD + Envelope): {len(files)} dosya...")
    
    advanced_records = []
    
    for idx, fpath in enumerate(files):
        data = load_single_ims_file(fpath)
        if data is None:
            continue
            
        sig_ch1 = data[:, 0]
        
        # 8.2. Wavelet Denoising
        clean_sig = wavelet_denoise(sig_ch1)
        
        # 8.4. EMD IMF Enerjileri
        _, imf_energies = compute_emd_imfs(clean_sig, max_imfs=3)
        
        # 8.3. Optimal Kurtogram bandı
        best_band, k_val = compute_fast_kurtogram(clean_sig)
        
        # 8.1. Zarf Analizi
        freqs, env_fft, envelope = compute_envelope_spectrum(
            clean_sig, lowcut=best_band[0], highcut=best_band[1]
        )
        
        def get_peak_in_range(target_f, tol=3.0):
            mask = (freqs >= target_f - tol) & (freqs <= target_f + tol)
            if np.any(mask):
                return np.max(env_fft[mask])
            return 0.0
            
        bpfo_env_peak = get_peak_in_range(BPFO)
        bpfi_env_peak = get_peak_in_range(BPFI)
        bsf_env_peak = get_peak_in_range(BSF)
        
        advanced_records.append({
            "file_idx": idx,
            "filename": fpath.name,
            "kurtogram_best_lowcut": best_band[0],
            "kurtogram_best_highcut": best_band[1],
            "kurtogram_max_kurtosis": k_val,
            "envelope_rms": np.sqrt(np.mean(envelope**2)),
            "envelope_bpfo_peak": bpfo_env_peak,
            "envelope_bpfi_peak": bpfi_env_peak,
            "envelope_bsf_peak": bsf_env_peak,
            "imf1_energy": imf_energies[0],
            "imf2_energy": imf_energies[1],
            "imf3_energy": imf_energies[2],
        })
        
    df_adv = pd.DataFrame(advanced_records)
    out_csv = PROCESSED_DATA_DIR / f"features_advanced_envelope_{test_name}.csv"
    df_adv.to_csv(out_csv, index=False)
    print(f"[SUCCESS] Gelismis sinyal isleme verileri kaydedildi: {out_csv}")
    return df_adv

if __name__ == "__main__":
    df_adv = extract_advanced_envelope_features("test2")
