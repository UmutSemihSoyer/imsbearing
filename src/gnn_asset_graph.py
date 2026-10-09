"""
IMS Graph Neural Network (GNN) & Cascading Failure Propagation Engine
Models mechanical asset dependency graphs and predicts multi-machine cascading failure propagation times.
"""

import os
import sys
import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Any, Tuple

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class GraphConvolutionLayer(nn.Module):
    """Simple Graph Convolutional Layer (GCN)."""
    def __init__(self, in_features: int, out_features: int):
        super(GraphConvolutionLayer, self).__init__()
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        nn.init.xavier_uniform_(self.weight)

    def forward(self, x, adj_matrix):
        # x: (num_nodes, in_features), adj_matrix: (num_nodes, num_nodes)
        support = torch.mm(x, self.weight)
        out = torch.spmm(adj_matrix, support)
        return out

class GNNAssetTopologyModel(nn.Module):
    """GNN Model predicting cascading structural stress across interconnected machinery."""
    def __init__(self, num_nodes: int = 4, feature_dim: int = 4):
        super(GNNAssetTopologyModel, self).__init__()
        self.gcn1 = GraphConvolutionLayer(feature_dim, 16)
        self.relu = nn.ReLU()
        self.gcn2 = GraphConvolutionLayer(16, 1) # Predicts cascading risk per node

    def forward(self, x, adj):
        h = self.relu(self.gcn1(x, adj))
        cascading_risk = self.gcn2(h, adj)
        return cascading_risk

class CascadingFailurePropagator:
    """Estimates time required for a primary bearing failure to propagate to connected gearbox/motor."""
    
    def predict_cascading_propagation(self, primary_asset_id: str, primary_rms: float,
                                      connected_assets: List[str]) -> Dict[str, Any]:
        """
        Calculates time-to-failure propagation (hours) to adjacent mechanical components.
        """
        # Baseline propagation velocity inversely proportional to primary RMS severity
        propagation_time_hours = float(max(1.0, 72.0 / (primary_rms * 10.0 + 1e-6)))

        results = {}
        for idx, target in enumerate(connected_assets):
            stage_delay = propagation_time_hours * (idx + 1)
            results[target] = {
                "estimated_failure_propagation_hours": round(stage_delay, 1),
                "cascading_risk_level": "HIGH" if stage_delay < 24.0 else "MODERATE"
            }

        return {
            "source_asset": primary_asset_id,
            "source_rms_g": primary_rms,
            "cascading_propagation_matrix": results
        }

if __name__ == "__main__":
    # Test GNN Topology Model
    nodes = 4 # Motor, Bearing 1, Bearing 2, Pump Impeller
    x_node_features = torch.tensor([
        [0.05, 3.0, 35.0, 1.0], # Motor
        [0.45, 7.8, 68.0, 0.3], # Bearing 1 (Failing)
        [0.12, 3.4, 40.0, 0.9], # Bearing 2
        [0.08, 3.1, 38.0, 0.95] # Pump
    ], dtype=torch.float32)

    # Mechanical Adjacency Matrix
    adj = torch.tensor([
        [1, 1, 0, 0],
        [1, 1, 1, 0],
        [0, 1, 1, 1],
        [0, 0, 1, 1]
    ], dtype=torch.float32)

    gnn = GNNAssetTopologyModel(num_nodes=nodes, feature_dim=4)
    cascading_scores = gnn(x_node_features, adj)

    print("[SUCCESS] GNN Topology Model Forward Pass completed.")
    print("GNN Node Cascading Risk Scores:", cascading_scores.detach().numpy().flatten())

    propagator = CascadingFailurePropagator()
    prop_res = propagator.predict_cascading_propagation("Bearing 1", 0.45, ["Gearbox Assembly", "Main Shaft", "Electric Motor"])
    print("Cascading Propagation Predictions:", prop_res)
