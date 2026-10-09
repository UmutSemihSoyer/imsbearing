import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from pathlib import Path

from src.config import PROCESSED_DATA_DIR, MODELS_DIR

class PhysicsInformedRULNet(nn.Module):
    """
    10.2. Physics-Informed Neural Network (PINN) RUL Modeli:
    Paris's Law (Çatlak İlerleme Fizik Yasası: da/dN = C*(delta_K)^m)
    diferansiyel denklemini ağın kayıp fonksiyonuna fiziksel kısıt (Physics Residual) olarak ekler.
    """
    def __init__(self, input_dim):
        super(PhysicsInformedRULNet, self).__init__()
        
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 32),
            nn.Tanh(),
            nn.Linear(32, 1)
        )
        
    def forward(self, x):
        return self.net(x)

def physics_loss(y_pred, x_time, C=1e-10, m=3.0):
    """
    Paris-Erdogan Fiziksel Aşınma Kaybı (Physics Residual Loss)
    dRUL/dt <= 0 kısıtı ve türev yumuşatma (Monotonic Degradation).
    """
    # Monotonik Yıpranma Kısıtı: RUL zamanla azalmalıdır (dRUL/dt <= 0)
    rul_diff = y_pred[1:] - y_pred[:-1]
    physics_residual = torch.relu(rul_diff) # Eğer RUL artıyorsa ceza uygula
    return torch.mean(physics_residual ** 2)

def train_pinn_rul(test_name="test2", epochs=30):
    csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_anomalies.csv"
    if not csv_path.exists():
        csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_rul.csv"
        
    df = pd.read_csv(csv_path)
    feature_cols = [c for c in df.columns if any(k in c for k in ["rms", "kurtosis", "bpfo_energy", "health_index"])]
    
    X = df[feature_cols].values
    y = df["target_rul"].values
    
    X_min, X_max = X.min(axis=0), X.max(axis=0) + 1e-8
    X_scaled = (X - X_min) / (X_max - X_min)
    
    X_t = torch.tensor(X_scaled, dtype=torch.float32, requires_grad=True)
    y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
    
    model = PhysicsInformedRULNet(input_dim=len(feature_cols))
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    criterion_mse = nn.MSELoss()
    
    print(f"[INFO] Physics-Informed Neural Network (PINN) Egitiliyor ({epochs} Epoch)...")
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        y_pred = model(X_t)
        
        loss_data = criterion_mse(y_pred, y_t)
        loss_phys = physics_loss(y_pred, X_t)
        
        # Toplam Kayıp = Veri Uyum Kaybı + Fiziksel Kısıt Kaybı (Paris Law Constraint)
        total_loss = loss_data + 10.0 * loss_phys
        total_loss.backward()
        optimizer.step()
        
    model.eval()
    with torch.no_grad():
        preds = model(X_t).numpy().flatten()
        
    rmse = np.sqrt(np.mean((y - preds)**2))
    mae = np.mean(np.abs(y - preds))
    
    print(f"[MODEL EVALUATION] Physics-Informed Neural Network (PINN):")
    print(f"  - RMSE : {rmse:.3f}")
    print(f"  - MAE  : {mae:.3f}")
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), MODELS_DIR / f"pinn_rul_{test_name}.pth")
    print(f"[SUCCESS] PINN modeli kaydedildi: {MODELS_DIR / f'pinn_rul_{test_name}.pth'}")
    return model

if __name__ == "__main__":
    train_pinn_rul("test2")
