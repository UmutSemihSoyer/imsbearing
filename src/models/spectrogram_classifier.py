"""
IMS Mel-Spectrogram Acoustic Fault Classifier (2D-CNN)
Converts raw acoustic microphone/vibration signals into 2D Spectrograms and classifies fault modes.
"""

import os
import sys
import numpy as np
from scipy.signal import spectrogram
import torch
import torch.nn as nn
import torch.optim as optim

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.config import FS, MODELS_DIR

class Spectrogram2DCNN(nn.Module):
    """2D Convolutional Neural Network for Spectrogram image classification."""
    def __init__(self, num_classes: int = 3):
        super(Spectrogram2DCNN, self).__init__()
        self.conv_block1 = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.conv_block2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.adaptive_pool = nn.AdaptiveAvgPool2d((8, 8))
        self.fc = nn.Sequential(
            nn.Linear(32 * 8 * 8, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        # x: (batch, 1, freq_bins, time_steps)
        out = self.conv_block1(x)
        out = self.conv_block2(out)
        out = self.adaptive_pool(out)
        out = out.view(out.size(0), -1)
        logits = self.fc(out)
        return logits

def signal_to_spectrogram(sig: np.ndarray, fs: float = FS) -> np.ndarray:
    """Computes normalized 2D Spectrogram log-power matrix from 1D vibration signal."""
    f, t, Sxx = spectrogram(sig, fs=fs, nperseg=256, noverlap=128)
    log_spec = np.log(Sxx + 1e-10)
    # Scale to [0, 1]
    norm_spec = (log_spec - log_spec.min()) / (log_spec.max() - log_spec.min() + 1e-8)
    return norm_spec

def train_spectrogram_classifier(epochs: int = 15):
    """Trains 2D-CNN model on synthetic spectrogram datasets."""
    print(f"[INFO] Generating Spectrogram dataset and training 2D-CNN Classifier ({epochs} Epochs)...")

    # Generate synthetic dataset for 3 classes (0: Normal, 1: BPFO, 2: BPFI)
    n_samples_per_class = 20
    specs, labels = [], []

    t = np.linspace(0, 1.0, int(FS), endpoint=False)

    for c in range(3):
        for _ in range(n_samples_per_class):
            if c == 0:
                sig = 0.05 * np.random.randn(len(t)) # Healthy
            elif c == 1:
                sig = 0.05 * np.random.randn(len(t)) + 0.3 * np.sin(2 * np.pi * 236.4 * t) # BPFO
            else:
                sig = 0.05 * np.random.randn(len(t)) + 0.3 * np.sin(2 * np.pi * 296.9 * t) # BPFI

            spec = signal_to_spectrogram(sig, FS)
            specs.append(spec)
            labels.append(c)

    X_data = torch.tensor(np.array(specs), dtype=torch.float32).unsqueeze(1) # (N, 1, H, W)
    y_data = torch.tensor(np.array(labels), dtype=torch.long)

    model = Spectrogram2DCNN(num_classes=3)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.003)

    model.train()
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        outputs = model(X_data)
        loss = criterion(outputs, y_data)
        loss.backward()
        optimizer.step()

        if epoch % 5 == 0 or epoch == epochs:
            print(f"Epoch {epoch:2d}/{epochs} | Loss: {loss.item():.4f}")

    output_path = os.path.join(MODELS_DIR, "spectrogram_2dcnn.pth")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save(model.state_dict(), output_path)

    print(f"[SUCCESS] 2D-CNN Spectrogram Classifier saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    train_spectrogram_classifier()
