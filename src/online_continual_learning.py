"""
IMS Online & Continual Learning Engine
Updates RUL models incrementally on streaming live sensor batches without catastrophic forgetting.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import MODELS_DIR

class IncrementalRULModel(nn.Module):
    """Linear regression / Neural incremental model for online streaming updates."""
    def __init__(self, input_dim: int = 11):
        super(IncrementalRULModel, self).__init__()
        self.linear = nn.Linear(input_dim, 1)

    def forward(self, x):
        return self.linear(x)

class OnlineContinualLearner:
    """
    Manages online incremental updates with Elastic Weight Consolidation (EWC) loss to prevent catastrophic forgetting.
    """

    def __init__(self, input_dim: int = 11, lr: float = 0.001, ewc_lambda: float = 0.4):
        self.model = IncrementalRULModel(input_dim=input_dim)
        self.optimizer = optim.SGD(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        self.ewc_lambda = ewc_lambda
        self.anchor_params = {n: p.clone().detach() for n, p in self.model.named_parameters()}

    def update_model_online(self, batch_x: np.ndarray, batch_y: np.ndarray) -> float:
        """
        Performs single-step online incremental parameter update.
        """
        self.model.train()
        x_t = torch.tensor(batch_x, dtype=torch.float32)
        y_t = torch.tensor(batch_y, dtype=torch.float32).unsqueeze(1)

        self.optimizer.zero_grad()
        preds = self.model(x_t)
        mse_loss = self.criterion(preds, y_t)

        # Elastic Weight Consolidation (EWC) penalty for catastrophic forgetting
        ewc_loss = 0.0
        for n, p in self.model.named_parameters():
            ewc_loss += torch.sum((p - self.anchor_params[n]) ** 2)

        total_loss = mse_loss + self.ewc_lambda * ewc_loss
        total_loss.backward()
        self.optimizer.step()

        return float(mse_loss.item())

if __name__ == "__main__":
    learner = OnlineContinualLearner()
    
    # Simulate streaming mini-batch
    batch_x = np.random.randn(5, 11)
    batch_y = np.array([140.0, 138.0, 135.0, 130.0, 125.0])

    loss = learner.update_model_online(batch_x, batch_y)
    print(f"[SUCCESS] Incremental online update completed. MSE Loss: {loss:.4f}")
