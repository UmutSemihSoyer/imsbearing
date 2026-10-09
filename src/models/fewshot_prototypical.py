"""
IMS Few-Shot & Zero-Shot Learning Engine (Prototypical Networks)
Classifies un-seen bearing model fault types using 1-2 signal support examples.
"""

import os
import sys
import torch
import torch.nn as nn
import numpy as np

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.config import MODELS_DIR

class PrototypicalNetworkEmbedding(nn.Module):
    """Embedding network mapping 1D vibration series into 16-D metric prototype space."""
    def __init__(self, input_dim: int = 11, embed_dim: int = 16):
        super(PrototypicalNetworkEmbedding, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Linear(32, embed_dim)
        )

    def forward(self, x):
        return self.encoder(x)

def compute_prototypes_and_classify(support_set: torch.Tensor, support_labels: torch.Tensor,
                                     query_set: torch.Tensor) -> torch.Tensor:
    """
    Computes class prototypes c_k in metric space and classifies query samples via Euclidean distance.
    """
    embedder = PrototypicalNetworkEmbedding(input_dim=11, embed_dim=16)
    embedder.eval()

    with torch.no_grad():
        support_embeds = embedder(support_set)
        query_embeds = embedder(query_set)

        unique_classes = torch.unique(support_labels)
        prototypes = []
        for c in unique_classes:
            class_mask = (support_labels == c)
            proto = torch.mean(support_embeds[class_mask], dim=0)
            prototypes.append(proto)

        prototypes = torch.stack(prototypes) # (n_classes, embed_dim)

        # Pairwise Euclidean distances
        dists = torch.cdist(query_embeds, prototypes)
        predicted_classes = torch.argmin(dists, dim=1)

    return predicted_classes

if __name__ == "__main__":
    # 2 support samples per class (3 classes: 0=Healthy, 1=BPFO, 2=BPFI)
    supp_x = torch.randn(6, 11)
    supp_y = torch.tensor([0, 0, 1, 1, 2, 2])
    query_x = torch.randn(4, 11)

    preds = compute_prototypes_and_classify(supp_x, supp_y, query_x)
    print(f"[SUCCESS] Few-Shot Prototypical Network Query Predictions: {preds.numpy()}")
