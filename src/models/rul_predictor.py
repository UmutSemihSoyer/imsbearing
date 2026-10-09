import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from pathlib import Path
from src.config import PROCESSED_DATA_DIR, MODELS_DIR, RESULTS_DIR

def train_rul_predictors(test_name="test2"):
    """
    Rulman RUL (Remaining Useful Life) değerini tahmin etmek için
    Random Forest ve XGBoost Regressor modellerini eğitir ve değerlendirir.
    """
    csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_anomalies.csv"
    if not csv_path.exists():
        csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_rul.csv"
        
    df = pd.read_csv(csv_path)
    
    # Girdi özellikleri (Features) ve Hedef (Target)
    feature_cols = [c for c in df.columns if any(k in c for k in ["rms", "kurtosis", "bpfo_energy", "peak_to_peak", "health_index"])]
    X = df[feature_cols].values
    y = df["target_rul"].values
    
    # Zaman serisi yapısını bozmamak için kronolojik bölme (%80 train, %20 test)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Random Forest Model
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    r2_rf = r2_score(y_test, y_pred_rf)
    
    print(f"[MODEL EVALUATION] Random Forest RUL Predictor:")
    print(f"  - RMSE : {rmse_rf:.3f}")
    print(f"  - MAE  : {mae_rf:.3f}")
    print(f"  - R²   : {r2_rf:.3f}")
    
    # Modeli kaydet
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf_model, MODELS_DIR / f"rf_rul_model_{test_name}.joblib")
    
    # Metrikleri kaydet
    metrics_df = pd.DataFrame([{
        "model": "RandomForestRegressor",
        "rmse": rmse_rf,
        "mae": mae_rf,
        "r2": r2_rf
    }])
    metrics_df.to_csv(RESULTS_DIR / "evaluation_metrics.csv", index=False)
    
    df["predicted_rul"] = rf_model.predict(X)
    df.to_csv(PROCESSED_DATA_DIR / f"final_predictions_{test_name}.csv", index=False)
    print(f"[SUCCESS] RUL Tahmin modeli kaydedildi ve final tahmin matrisi yazildi.")
    return df

if __name__ == "__main__":
    train_rul_predictors("test2")
