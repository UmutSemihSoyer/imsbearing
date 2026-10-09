import os
from pathlib import Path

# Proje Kök Dizin Yolu
BASE_DIR = Path(__file__).resolve().parent.parent

# Alt Dizin Yolları
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Dizinlerin varlığından emin olma
for d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, RESULTS_DIR, DASHBOARD_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# IMS Veri Seti Parametreleri
SAMPLING_RATE = 20000  # 20 kHz (Hz)
FS = SAMPLING_RATE     # Alias for Sampling Rate
SAMPLES_PER_FILE = 20480  # Her 1 saniyelik kayıt için örnek sayısı
SHAFT_SPEED_RPM = 2000  # Dönüş hızı (RPM)
SHAFT_SPEED_HZ = SHAFT_SPEED_RPM / 60.0  # 33.33 Hz

# Rulman Geometrik Özellikleri (Rexnord ZA-2115)
N_ROLLERS = 16  # Bilya / Makara sayısı
ROLLER_DIAMETER_INCH = 0.331  # Bilya çapı (d)
PITCH_DIAMETER_INCH = 2.815   # Hatve çapı (D)
CONTACT_ANGLE_DEG = 15.17     # Temas açısı (alfa)

# Teorik Karakteristik Arıza Frekansları (Hz)
BPFO = 236.4  # Outer Race Fault Frequency
BPFI = 296.9  # Inner Race Fault Frequency
BSF = 139.9   # Ball/Roller Spin Frequency
FTF = 14.7    # Cage (Fundamental Train) Frequency

BEARING_FREQS = {
    "BPFO": BPFO,
    "BPFI": BPFI,
    "BSF": BSF,
    "FTF": FTF
}

# Aşınma & Sağlık Eşikleri
DEGRADATION_THRESHOLDS = {
    "rms_warning": 0.25,
    "rms_critical": 0.50,
    "kurtosis_warning": 4.5,
    "kurtosis_critical": 8.0
}


# Test Seti Yapılandırmaları
TEST_CONFIGS = {
    "test1": {
        "channels": 8,
        "bearings": {
            "bearing1_x": 0, "bearing1_y": 1,
            "bearing2_x": 2, "bearing2_y": 3,
            "bearing3_x": 4, "bearing3_y": 5,
            "bearing4_x": 6, "bearing4_y": 7,
        },
        "description": "35 Gün / 2156 Dosya (Bearing 3 Inner race, Bearing 4 Roller element fault)"
    },
    "test2": {
        "channels": 4,
        "bearings": {
            "bearing1": 0,
            "bearing2": 1,
            "bearing3": 2,
            "bearing4": 3,
        },
        "description": "7 Gün / 984 Dosya (Bearing 1 Outer race fault)"
    },
    "test3": {
        "channels": 4,
        "bearings": {
            "bearing1": 0,
            "bearing2": 1,
            "bearing3": 2,
            "bearing4": 3,
        },
        "description": "44 Gün / 6324 Dosya (Bearing 3 Outer race fault)"
    }
}
