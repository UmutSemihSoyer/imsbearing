import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from src.config import RAW_DATA_DIR, TEST_CONFIGS

def get_sorted_file_list(test_dir):
    """
    Belirtilen test dizinindeki tüm zaman serisi dosyalarını kronolojik
    olarak sıralı şekilde getirir.
    """
    path = Path(test_dir)
    if not path.exists():
        raise FileNotFoundError(f"Dizin bulunamadı: {test_dir}")
        
    files = [f for f in path.iterdir() if f.is_file() and not f.name.startswith(".")]
    
    # Dosya isimleri timestamp formatında olduğu için string sıralama kronolojiktir
    sorted_files = sorted(files, key=lambda x: x.name)
    return sorted_files

def parse_file_timestamp(filename):
    """
    IMS dosya adından (Örn: '2004.02.12.10.30.00') datetime objesi türetir.
    """
    try:
        return datetime.strptime(filename, "%Y.%m.%d.%H.%M.%S")
    except ValueError:
        return None

def load_single_ims_file(file_path, num_channels=4):
    """
    Tek bir IMS 1-saniyelik ivmeölçer dosyasını (tab ile ayrılmış) okur.
    Döndürülen değer: numpy array (n_samples, n_channels)
    """
    try:
        data = pd.read_csv(file_path, sep="\t", header=None).values
        return data
    except Exception as e:
        print(f"Hata: {file_path} dosyası okunamadı. Detay: {e}")
        return None

if __name__ == "__main__":
    demo_dir = RAW_DATA_DIR / "test2"
    if demo_dir.exists():
        files = get_sorted_file_list(demo_dir)
        print(f"[INFO] Tespit edilen dosya sayisi: {len(files)}")
        if len(files) > 0:
            sample_data = load_single_ims_file(files[0])
            print(f"[INFO] Ilk dosya sekli (shape): {sample_data.shape}")
