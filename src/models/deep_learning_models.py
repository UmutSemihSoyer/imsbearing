import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from src.config import PROCESSED_DATA_DIR, MODELS_DIR, RESULTS_DIR

# 1D-CNN + BiLSTM + Attention PyTorch Derin Öğrenme Mimarisi
class AttentionLayer(nn.Module):
    def __init__(self, hidden_dim):
        super(AttentionLayer, self).__init__()
        self.attn = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1)
        )
        
    def forward(self, lstm_output):
        # lstm_output shape: (batch_size, seq_len, hidden_dim)
        attn_weights = self.attn(lstm_output) # (batch_size, seq_len, 1)
        attn_weights = torch.softmax(attn_weights, dim=1)
        context_vector = torch.sum(attn_weights * lstm_output, dim=1) # (batch_size, hidden_dim)
        return context_vector, attn_weights

class CNN_BiLSTM_Attention_RUL(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_layers=2):
        super(CNN_BiLSTM_Attention_RUL, self).__init__()
        
        # 1D-CNN Katmanı (Uzamsal/Frekans Özellik Çıkarımı)
        self.conv1 = nn.Conv1d(in_channels=input_dim, out_channels=32, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        
        # BiLSTM Katmanı (Zamansal Dizisel Bellek)
        self.bilstm = nn.LSTM(
            input_size=32,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )
        
        # Attention Katmanı
        self.attention = AttentionLayer(hidden_dim * 2)
        
        # Tam Bağlantılı Çıkış Katmanı (RUL Regression)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1)
        )
        
    def forward(self, x):
        # x shape: (batch_size, seq_len, input_dim)
        # 1D Conv için transpoze: (batch_size, input_dim, seq_len)
        x_conv = x.transpose(1, 2)
        conv_out = self.pool(self.relu(self.conv1(x_conv)))
        
        # LSTM için tekrar transpoze: (batch_size, seq_len_pooled, 32)
        conv_out = conv_out.transpose(1, 2)
        
        lstm_out, _ = self.bilstm(conv_out)
        context, _ = self.attention(lstm_out)
        
        rul_pred = self.fc(context)
        return rul_pred

def prepare_sequences(X, y, seq_len=10):
    """
    Zaman serisi verisini pencereleme (sliding window) yöntemiyle sekanslara ayırır.
    """
    X_seq, y_seq = [], []
    for i in range(len(X) - seq_len + 1):
        X_seq.append(X[i:i+seq_len])
        y_seq.append(y[i+seq_len-1])
    return np.array(X_seq), np.array(y_seq)

def train_deep_learning_rul(test_name="test2", epochs=30, seq_len=10):
    """
    Aşama 9.1: 1D-CNN + BiLSTM + Attention Derin Öğrenme Modeli Eğitimi
    """
    csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_anomalies.csv"
    if not csv_path.exists():
        csv_path = PROCESSED_DATA_DIR / f"processed_{test_name}_with_rul.csv"
        
    df = pd.read_csv(csv_path)
    
    # Özellik kolonları
    feature_cols = [c for c in df.columns if any(k in c for k in ["rms", "kurtosis", "bpfo_energy", "health_index"])]
    X = df[feature_cols].values
    y = df["target_rul"].values
    
    # Min-Max Normalizasyonu
    X_min, X_max = X.min(axis=0), X.max(axis=0) + 1e-8
    X_scaled = (X - X_min) / (X_max - X_min)
    
    # Sekans oluşturma
    X_seq, y_seq = prepare_sequences(X_scaled, y, seq_len=seq_len)
    
    # Train / Test bölme (%80 train, %20 test)
    split_idx = int(len(X_seq) * 0.8)
    X_train, X_test = X_seq[:split_idx], X_seq[split_idx:]
    y_train, y_test = y_seq[:split_idx], y_seq[split_idx:]
    
    # Tensor Dönüştürme
    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)
    
    dataset = TensorDataset(X_train_t, y_train_t)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    input_dim = len(feature_cols)
    model = CNN_BiLSTM_Attention_RUL(input_dim=input_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.003)
    
    print(f"[INFO] 1D-CNN + BiLSTM + Attention RUL Modeli egitiliyor ({epochs} Epoch)...")
    model.train()
    for epoch in range(epochs):
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()
            
    # Test Değerlendirmesi
    model.eval()
    with torch.no_grad():
        test_preds = model(X_test_t).numpy().flatten()
        
    rmse = np.sqrt(np.mean((y_test - test_preds)**2))
    mae = np.mean(np.abs(y_test - test_preds))
    
    print(f"[MODEL EVALUATION] 1D-CNN + BiLSTM + Attention RUL Predictor:")
    print(f"  - RMSE : {rmse:.3f}")
    print(f"  - MAE  : {mae:.3f}")
    
    # Modeli kaydet
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), MODELS_DIR / f"cnn_bilstm_attn_rul_{test_name}.pth")
    print(f"[SUCCESS] Derin Ogrenme RUL modeli kaydedildi: {MODELS_DIR / f'cnn_bilstm_attn_rul_{test_name}.pth'}")
    return model

if __name__ == "__main__":
    train_deep_learning_rul("test2")
