import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from src.config import PROCESSED_DATA_DIR, MODELS_DIR

def train_anomaly_detectors(test_name="test2", baseline_samples=20):
    """
    Normal/Sağlıklı dönem verisiyle (ilk baseline_samples dosya) Isolation Forest
    ve One-Class SVM modellerini eğitir ve kaydeder.
    """
    csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_rul.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"İşlenmiş veri bulunamadı: {csv_path}")
        
    df = pd.read_csv(csv_path)
    
    # Özellik kolonlarını seç (Zaman ve frekans alanı parametreleri)
    feature_cols = [c for c in df.columns if any(k in c for k in ["rms", "kurtosis", "bpfo_energy", "peak_to_peak"])]
    X = df[feature_cols].values
    
    # Sadece ilk 20 numune (sağlıklı evre) ile modeller eğitilir
    X_train = X[:baseline_samples]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_scaled = scaler.transform(X)
    
    # 1. Isolation Forest
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    iso_forest.fit(X_train_scaled)
    iso_preds = iso_forest.predict(X_scaled)  # 1: Normal, -1: Anomali
    
    # 2. One-Class SVM
    oc_svm = OneClassSVM(nu=0.05, kernel="rbf", gamma="scale")
    oc_svm.fit(X_train_scaled)
    oc_svm_preds = oc_svm.predict(X_scaled)
    
    df["anomaly_iso_forest"] = np.where(iso_preds == -1, 1, 0)
    df["anomaly_oc_svm"] = np.where(oc_svm_preds == -1, 1, 0)
    
    # Modelleri kaydet
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, MODELS_DIR / f"scaler_{test_name}.joblib")
    joblib.dump(iso_forest, MODELS_DIR / f"iso_forest_{test_name}.joblib")
    joblib.dump(oc_svm, MODELS_DIR / f"oc_svm_{test_name}.joblib")
    
    output_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_anomalies.csv"
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Anomali tespit modelleri egitildi ve kaydedildi: {output_path}")
    return df

if __name__ == "__main__":
    df_anom = train_anomaly_detectors("test2")
