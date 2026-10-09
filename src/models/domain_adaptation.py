import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from pathlib import Path

from src.config import PROCESSED_DATA_DIR, MODELS_DIR

def guassian_kernel(source, target, kernel_mul=2.0, kernel_num=5, fix_sigma=None):
    """
    MMD (Maximum Mean Discrepancy) için Gauss Çekirdek Matrisi hesaplar.
    """
    n_samples = int(source.size(0)) + int(target.size(0))
    total = torch.cat([source, target], dim=0)
    
    total0 = total.unsqueeze(0).expand(int(total.size(0)), int(total.size(0)), int(total.size(1)))
    total1 = total.unsqueeze(1).expand(int(total.size(0)), int(total.size(0)), int(total.size(1)))
    L2_distance = ((total0-total1)**2).sum(2)
    
    if fix_sigma:
        bandwidth = fix_sigma
    else:
        bandwidth = torch.sum(L2_distance.data) / (n_samples**2 - n_samples)
    bandwidth /= kernel_mul ** (kernel_num // 2)
    bandwidth_list = [bandwidth * (kernel_mul**i) for i in range(kernel_num)]
    
    kernel_val = [torch.exp(-L2_distance / bandwidth_temp) for bandwidth_temp in bandwidth_list]
    return sum(kernel_val)

def mmd_loss(source, target):
    """
    Source ve Target dağılımları arasındaki Maximum Mean Discrepancy (MMD) kaybını hesaplar.
    """
    batch_size = int(source.size(0))
    kernels = guassian_kernel(source, target)
    XX = kernels[:batch_size, :batch_size]
    YY = kernels[batch_size:, batch_size:]
    XY = kernels[:batch_size, batch_size:]
    YX = kernels[batch_size:, :batch_size]
    loss = torch.mean(XX + YY - XY - YX)
    return loss

class DomainAdaptationRUL(nn.Module):
    """
    9.3. Alan Uyarlamalı (Domain Adaptation) Derin RUL Tahmin Modeli (DA-CNN)
    """
    def __init__(self, input_dim):
        super(DomainAdaptationRUL, self).__init__()
        
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU()
        )
        
        self.regressor = nn.Sequential(
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )
        
    def forward(self, source, target=None):
        source_feat = self.feature_extractor(source)
        source_pred = self.regressor(source_feat)
        
        if target is not None:
            target_feat = self.feature_extractor(target)
            mmd = mmd_loss(source_feat, target_feat)
            return source_pred, mmd
            
        return source_pred

def train_domain_adaptation(test_source="test2", test_target="test2"):
    csv_path = PROCESSED_DATA_DIR / f"processed_{test_source}_with_anomalies.csv"
    if not csv_path.exists():
        csv_path = PROCESSED_DATA_DIR / f"processed_{test_source}_with_rul.csv"
        
    df = pd.read_csv(csv_path)
    feature_cols = [c for c in df.columns if any(k in c for k in ["rms", "kurtosis", "bpfo_energy", "health_index"])]
    
    X_src = df[feature_cols].values
    y_src = df["target_rul"].values
    
    # Min-Max
    X_src_scaled = (X_src - X_src.min(axis=0)) / (X_src.max(axis=0) - X_src.min(axis=0) + 1e-8)
    
    # Hedef alan olarak hafif gürültülü alan ekleme (Domain shift simülasyonu)
    X_tgt_scaled = X_src_scaled + np.random.normal(0, 0.05, X_src_scaled.shape)
    
    X_src_t = torch.tensor(X_src_scaled, dtype=torch.float32)
    y_src_t = torch.tensor(y_src, dtype=torch.float32).unsqueeze(1)
    X_tgt_t = torch.tensor(X_tgt_scaled, dtype=torch.float32)
    
    model = DomainAdaptationRUL(input_dim=len(feature_cols))
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    criterion_mse = nn.MSELoss()
    
    print(f"[INFO] Domain Adaptation (DA-CNN) Modeli egitiliyor...")
    model.train()
    for epoch in range(25):
        optimizer.zero_grad()
        preds_src, loss_mmd = model(X_src_t, X_tgt_t)
        loss_mse = criterion_mse(preds_src, y_src_t)
        total_loss = loss_mse + 0.2 * loss_mmd
        total_loss.backward()
        optimizer.step()
        
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), MODELS_DIR / f"domain_adaptation_rul_{test_source}.pth")
    print(f"[SUCCESS] Domain Adaptation modeli kaydedildi: {MODELS_DIR / f'domain_adaptation_rul_{test_source}.pth'}")
    return model

if __name__ == "__main__":
    train_domain_adaptation("test2", "test2")
