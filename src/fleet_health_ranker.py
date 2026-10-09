"""
IMS Fleet Health Ranking Engine
Ranks hundreds of industrial fleet bearings across manufacturing lines to isolate top critical equipment requiring immediate shutdown.
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import List, Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import RESULTS_DIR

class FleetHealthRanker:
    """
    Evaluates enterprise fleet health and isolates top 5 highest-risk assets.
    """

    def rank_fleet_assets(self, fleet_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Ranks fleet bearings by failure risk score combining RMS, Kurtosis, and predicted RUL.
        """
        records = []
        for asset in fleet_data:
            rms = asset["rms"]
            kurt = asset["kurtosis"]
            rul = asset["predicted_rul"]

            # Composite Risk Score (higher = more critical)
            risk_score = float((rms * 100.0) + (kurt * 10.0) + (200.0 / max(0.1, rul)))

            records.append({
                "asset_id": asset["asset_id"],
                "plant_line": asset.get("line", "Line 1"),
                "rms_g": rms,
                "kurtosis": kurt,
                "predicted_rul_hours": rul,
                "composite_risk_score": round(risk_score, 2),
                "urgency_rank": 0
            })

        df_ranked = pd.DataFrame(records).sort_values(by="composite_risk_score", ascending=False).reset_index(drop=True)
        df_ranked["urgency_rank"] = df_ranked.index + 1

        output_csv = os.path.join(RESULTS_DIR, "fleet_critical_ranking.csv")
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df_ranked.to_csv(output_csv, index=False)

        print(f"[SUCCESS] Fleet Health Ranking complete. Top critical asset: {df_ranked['asset_id'].iloc[0]}")
        return df_ranked

if __name__ == "__main__":
    ranker = FleetHealthRanker()
    demo_fleet = [
        {"asset_id": "BRG-LINE1-PUMP1", "line": "High Pressure Line 1", "rms": 0.08, "kurtosis": 3.1, "predicted_rul": 150.0},
        {"asset_id": "BRG-LINE2-COMP1", "line": "Air Compression Line 2", "rms": 0.29, "kurtosis": 5.8, "predicted_rul": 40.0},
        {"asset_id": "BRG-LINE3-TURB1", "line": "Power Turbine Line 3", "rms": 0.68, "kurtosis": 9.8, "predicted_rul": 6.2},
        {"asset_id": "BRG-LINE1-PUMP2", "line": "High Pressure Line 1", "rms": 0.12, "kurtosis": 3.5, "predicted_rul": 110.0},
        {"asset_id": "BRG-LINE4-FAN1", "line": "Exhaust Fan Line 4", "rms": 0.45, "kurtosis": 7.2, "predicted_rul": 15.0}
    ]
    df_result = ranker.rank_fleet_assets(demo_fleet)
    print(df_result[["urgency_rank", "asset_id", "composite_risk_score", "predicted_rul_hours"]])
