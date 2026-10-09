import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import math
from pathlib import Path

from src.config import PROCESSED_DATA_DIR, MODELS_DIR

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0) # (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1)]
        return x

class Transformer_Informer_RUL(nn.Module):
    """
    9.2. Transformer / Informer tabanlı Zaman Serisi RUL Tahmin Modeli
    """
    def __init__(self, input_dim, d_model=64, nhead=4, num_layers=2):
        super(Transformer_Informer_RUL, self).__init__()
        
        self.input_projection = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=128,
            dropout=0.1,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.fc_out = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        
    def forward(self, x):
        # x: (batch_size, seq_len, input_dim)
        x_proj = self.input_projection(x)
        x_pe = self.pos_encoder(x_proj)
        
        out = self.transformer_encoder(x_pe)
        # Son zaman adımının çıktısını al
        last_step = out[:, -1, :]
        rul_pred = self.fc_out(last_step)
        return rul_pred

def train_transformer_rul(test_name="test2", epochs=30, seq_len=10):
    csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_anomalies.csv"
    if not csv_path.exists():
        csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_rul.csv"
        
    df = pd.read_csv(csv_path)
    
    feature_cols = [c for c in df.columns if any(k in c for k in ["rms", "kurtosis", "bpfo_energy", "health_index"])]
    X = df[feature_cols].values
    y = df["target_rul"].values
    
    X_min, X_max = X.min(axis=0), X.max(axis=0) + 1e-8
    X_scaled = (X - X_min) / (X_max - X_min)
    
    X_seq, y_seq = [], []
    for i in range(len(X_scaled) - seq_len + 1):
        X_seq.append(X_scaled[i:i+seq_len])
        y_seq.append(y[i+seq_len-1])
        
    X_seq, y_seq = np.array(X_seq), np.array(y_seq)
    split_idx = int(len(X_seq) * 0.8)
    
    X_train_t = torch.tensor(X_seq[:split_idx], dtype=torch.float32)
    y_train_t = torch.tensor(y_seq[:split_idx], dtype=torch.float32).unsqueeze(1)
    X_test_t = torch.tensor(X_seq[split_idx:], dtype=torch.float32)
    y_test_t = torch.tensor(y_seq[split_idx:], dtype=torch.float32).unsqueeze(1)
    
    dataset = TensorDataset(X_train_t, y_train_t)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    model = Transformer_Informer_RUL(input_dim=len(feature_cols))
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.002)
    
    print(f"[INFO] Transformer Informer RUL Modeli egitiliyor ({epochs} Epoch)...")
    model.train()
    for epoch in range(epochs):
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()
            
    model.eval()
    with torch.no_grad():
        test_preds = model(X_test_t).numpy().flatten()
        
    rmse = np.sqrt(np.mean((y_seq[split_idx:] - test_preds)**2))
    mae = np.mean(np.abs(y_seq[split_idx:] - test_preds))
    
    print(f"[MODEL EVALUATION] Transformer Informer RUL Predictor:")
    print(f"  - RMSE : {rmse:.3f}")
    print(f"  - MAE  : {mae:.3f}")
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), MODELS_DIR / f"transformer_rul_{test_name}.pth")
    print(f"[SUCCESS] Transformer RUL modeli kaydedildi: {MODELS_DIR / f'transformer_rul_{test_name}.pth'}")
    return model

if __name__ == "__main__":
    train_transformer_rul("test2")
