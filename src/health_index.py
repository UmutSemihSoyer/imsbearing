import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import mahalanobis
from pathlib import Path
from src.config import PROCESSED_DATA_DIR

def calculate_health_index_pca(df_features, feature_cols=None):
    """
    Özellik matrisinden PCA (Temel Bileşen Analizi) kullanarak 1.0 (Sağlıklı) ile
    0.0 (Kritik Arıza) arasında ölçeklenmiş Sağlık İndeksi (Health Index - HI) hesaplar.
    """
    if feature_cols is None:
        # RMS, Kurtosis ve BPFO enerji kolonlarını seç
        feature_cols = [c for c in df_features.columns if any(k in c for k in ["rms", "kurtosis", "bpfo_energy", "peak_to_peak"])]
        
    X = df_features[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    pca = PCA(n_components=1)
    pc1 = pca.fit_transform(X_scaled).flatten()
    
    # PC1 değerini 0 ile 1 arasına normalize et (Ters ilişkiyi düzelt)
    hi = (pc1 - np.min(pc1)) / (np.max(pc1) - np.min(pc1) + 1e-12)
    
    # Başlangıçta sağlıklı (1.0), sonda bozuk (0.0) olacak şekilde yönlendir
    if hi[0] < hi[-1]:
        hi = 1.0 - hi
        
    return hi

def calculate_mahalanobis_hi(df_features, baseline_samples=20, feature_cols=None):
    """
    Normal çalışma evresinden (ilk baseline_samples kadar dosya) Mahalanobis mesafesi hesabı.
    """
    if feature_cols is None:
        feature_cols = [c for c in df_features.columns if any(k in c for k in ["rms", "kurtosis", "bpfo_energy"])]
        
    X = df_features[feature_cols].values
    baseline_X = X[:baseline_samples]
    
    mean_baseline = np.mean(baseline_X, axis=0)
    cov_baseline = np.cov(baseline_X, rowvar=False) + 1e-6 * np.eye(len(feature_cols))
    inv_cov = np.linalg.inv(cov_baseline)
    
    distances = []
    for row in X:
        d = mahalanobis(row, mean_baseline, inv_cov)
        distances.append(d)
        
    distances = np.array(distances)
    # Mesafeyi 1.0 -> 0.0 aralığına düşür
    hi_mahalanobis = np.exp(-0.2 * distances)
    return hi_mahalanobis

def process_degradation_and_rul(test_name="test2"):
    """
    Özellik CSV dosyasını okur, Sağlık İndeksini (HI), Yıpranma Durumunu (State) ve
    hedef RUL (Kalan Faydalı Ömür) kolonlarını ekleyip kaydeder.
    """
    csv_path = PROCESSED_DATA_DIR / f"features_{test_name}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Özellik dosyası bulunamadı: {csv_path}")
        
    df = pd.read_csv(csv_path)
    
    # 1. PCA ve Mahalanobis Sağlık İndeksi
    df["health_index_pca"] = calculate_health_index_pca(df)
    df["health_index_mahalanobis"] = calculate_mahalanobis_hi(df)
    
    # 2. Rulmanın Durumunu Etiketleme (Health State)
    def assign_state(hi):
        if hi >= 0.75:
            return "Normal"
        elif hi >= 0.35:
            return "Warning"
        else:
            return "Critical"
            
    df["health_state"] = df["health_index_pca"].apply(assign_state)
    
    # 3. Hedef RUL (Kalan Faydalı Ömür - Adım Sayısı Olarak)
    total_steps = len(df)
    df["target_rul"] = total_steps - 1 - df["file_idx"]
    df["target_rul_percent"] = (df["target_rul"] / (total_steps - 1)) * 100.0
    
    output_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_rul.csv"
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Islenmis veri ve RUL hedef matrisi kaydedildi: {output_path}")
    return df

if __name__ == "__main__":
    df_processed = process_degradation_and_rul("test2")
