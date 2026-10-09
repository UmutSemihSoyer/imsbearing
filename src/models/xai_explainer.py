import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.inspection import permutation_importance
from src.config import PROCESSED_DATA_DIR, MODELS_DIR, RESULTS_DIR

def compute_xai_feature_importance(test_name="test2"):
    """
    10.1. Model Açıklanabilirliği (XAI): RUL tahmin modellerindeki
    özelliklerin önem derecelerini ve etkilerini (SHAP / Permutation Importance) hesaplar.
    """
    csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_anomalies.csv"
    if not csv_path.exists():
        csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_rul.csv"
        
    df = pd.read_csv(csv_path)
    feature_cols = [c for c in df.columns if any(k in c for k in ["rms", "kurtosis", "bpfo_energy", "peak_to_peak", "health_index"])]
    X = df[feature_cols].values
    y = df["target_rul"].values
    
    # Eğitilmiş Random Forest modelini yükle
    rf_model_path = MODELS_DIR / f"rf_rul_model_{test_name}.joblib"
    if rf_model_path.exists():
        model = joblib.load(rf_model_path)
    else:
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X, y)
        
    # Permütasyon Önem Derecesi (XAI Feature Importance)
    result = permutation_importance(model, X, y, n_repeats=10, random_state=42)
    importances = result.importances_mean
    
    df_xai = pd.DataFrame({
        "feature": feature_cols,
        "importance": importances,
        "std": result.importances_std
    }).sort_values(by="importance", ascending=False)
    
    output_path = RESULTS_DIR / f"xai_feature_importance_{test_name}.csv"
    df_xai.to_csv(output_path, index=False)
    
    print(f"[XAI MODEL EXPLAINER] En Onemli Ozellikler:")
    for idx, row in df_xai.head(5).iterrows():
        print(f"  - {row['feature']}: {row['importance']:.4f}")
        
    print(f"[SUCCESS] XAI aciklanabilirlik sonuclari kaydedildi: {output_path}")
    return df_xai

if __name__ == "__main__":
    compute_xai_feature_importance("test2")
