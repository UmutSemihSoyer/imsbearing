import os
import urllib.request
import zipfile
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.config import RAW_DATA_DIR, SAMPLING_RATE, SAMPLES_PER_FILE, BPFO, BPFI

# NASA IMS Bearing dataset direct public download URLs / Mirrors
NASA_IMS_URLS = {
    "test1": "https://raw.githubusercontent.com/zhou-group/Bearing-Dataset-NASA/master/2nd_test.zip", # Popular mirror
    "test2": "https://raw.githubusercontent.com/zhou-group/Bearing-Dataset-NASA/master/2nd_test.zip"
}

def create_synthetic_demo_data(test_name="test2", num_files=100):
    """
    Eğer gerçek veri seti henüz indirilmediyse, test ve pipeline geliştirmek
    için 100 adet sentetik IMS rulman yıpranma sinyali üretir.
    Rulman zamanla (dosya indeksi arttıkça) normal durumdan BPFO (dış bilezik) arızasına geçer.
    """
    output_dir = RAW_DATA_DIR / test_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[DATA] Sentetik Gosterim Veri Seti Olusturuluyor: {test_name} ({num_files} dosya)...")
    
    start_time = datetime(2004, 2, 12, 10, 30, 0)
    t = np.linspace(0, 1.0, SAMPLES_PER_FILE, endpoint=False)
    
    for i in range(num_files):
        timestamp_str = (start_time + timedelta(minutes=10 * i)).strftime("%Y.%m.%d.%H.%M.%S")
        file_path = output_dir / timestamp_str
        
        # Degradation factor: 0 (healthy) -> 1 (failed)
        degradation = (i / num_files) ** 3
        
        # Base noise
        noise = np.random.normal(0, 0.05 + 0.1 * degradation, SAMPLES_PER_FILE)
        
        # Healthy background signal (Shaft rotational frequency ~33.33 Hz)
        shaft_signal = 0.1 * np.sin(2 * np.pi * 33.33 * t)
        
        # Fault signal (BPFO ~236.4 Hz impacts with damping)
        fault_signal = np.zeros(SAMPLES_PER_FILE)
        if i > 20: # Degradation starts after snapshot 20
            impact_period = int(SAMPLING_RATE / BPFO)
            num_impacts = SAMPLES_PER_FILE // impact_period
            for imp in range(num_impacts):
                idx = imp * impact_period
                decay = np.exp(-np.linspace(0, 5, 200))
                imp_len = min(200, SAMPLES_PER_FILE - idx)
                fault_signal[idx:idx+imp_len] += degradation * 2.5 * np.sin(2 * np.pi * 2000 * t[:imp_len]) * decay[:imp_len]
        
        # Combine signals for 4 channels
        ch1 = shaft_signal + fault_signal + noise
        ch2 = shaft_signal * 0.8 + noise * 0.9
        ch3 = shaft_signal * 0.7 + noise * 0.85
        ch4 = shaft_signal * 0.75 + noise * 0.88
        
        # Stack channels into tab-separated values (like original IMS dataset format)
        data_matrix = np.column_stack([ch1, ch2, ch3, ch4])
        np.savetxt(file_path, data_matrix, fmt="%.6f", delimiter="\t")
        
    print(f"[SUCCESS] {num_files} adet sentetik IMS veri dosyasi '{output_dir}' dizinine yazildi.")

if __name__ == "__main__":
    create_synthetic_demo_data("test2", num_files=100)
