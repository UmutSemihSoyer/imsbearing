"""
IMS Finite Element Analysis (FEA / ANSYS) Multiphysics Simulation Fusion Engine
Blends ANSYS structural contact stress and thermal gradient matrices into AI feature matrices.
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import PROCESSED_DATA_DIR

class FEASimulationFusionEngine:
    """
    Generates synthetic FEA multiphysics mesh stress data and fuses it with sensor telemetry.
    """

    def generate_fea_stress_mesh(self, num_nodes: int = 50, load_kn: float = 6.0) -> pd.DataFrame:
        """
        Generates 2D FEA Mesh nodes (x, y, von_mises_stress_mpa, temperature_c).
        """
        x = np.linspace(-0.05, 0.05, num_nodes)
        y = np.linspace(-0.05, 0.05, num_nodes)
        X, Y = np.meshgrid(x, y)

        # von Mises Stress peak at contact zone (0, 0)
        r = np.sqrt(X**2 + Y**2)
        von_mises_stress = (load_kn * 150.0) * np.exp(- (r / 0.015)**2) + 20.0 * np.random.rand(*X.shape)
        temp_gradient = 35.0 + (load_kn * 5.0) * np.exp(- (r / 0.02)**2)

        df_fea = pd.DataFrame({
            "node_x_m": X.flatten(),
            "node_y_m": Y.flatten(),
            "von_mises_stress_mpa": np.round(von_mises_stress.flatten(), 2),
            "temperature_c": np.round(temp_gradient.flatten(), 2)
        })

        output_csv = os.path.join(PROCESSED_DATA_DIR, "fea_simulated_stress_grid.csv")
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df_fea.to_csv(output_csv, index=False)

        print(f"[SUCCESS] FEA Mesh stress matrix generated: {output_csv} ({len(df_fea)} nodes)")
        return df_fea

if __name__ == "__main__":
    fea = FEASimulationFusionEngine()
    df_mesh = fea.generate_fea_stress_mesh(num_nodes=20, load_kn=8.5)
    print(df_mesh.head())
