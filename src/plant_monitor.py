"""
IMS Multi-Asset Plant Monitoring & Fleet Analytics System
Aggregates health indices across multiple machines/bearings to compute plant risk scores and prioritize maintenance schedules.
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import List, Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import DEGRADATION_THRESHOLDS

class PlantFleetMonitor:
    """
    Manages multi-bearing fleet topology across industrial production lines.
    """

    def __init__(self, plant_name: str = "Industrial Processing Plant #1"):
        self.plant_name = plant_name
        self.assets = [
            {"asset_id": "PUMP-01-BRG1", "line": "Line 1: High Pressure Pump", "location": "Drive End (DE)", "rms": 0.082, "kurtosis": 3.1, "predicted_rul": 155.0},
            {"asset_id": "PUMP-01-BRG2", "line": "Line 1: High Pressure Pump", "location": "Non-Drive End (NDE)", "rms": 0.076, "kurtosis": 2.9, "predicted_rul": 160.0},
            {"asset_id": "COMP-02-BRG3", "line": "Line 2: Air Compressor", "location": "Input Shaft", "rms": 0.285, "kurtosis": 5.4, "predicted_rul": 42.0},
            {"asset_id": "TURB-03-BRG4", "line": "Line 3: Power Turbine", "location": "Exhaust Housing", "rms": 0.620, "kurtosis": 9.1, "predicted_rul": 8.5}
        ]

    def compute_asset_status(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates Health Index (0-1), status category, and priority score for a single asset."""
        rms = asset["rms"]
        kurt = asset["kurtosis"]
        rul = asset["predicted_rul"]

        # Health Index calculation (1.0 healthy -> 0.0 critical)
        hi = float(np.clip(rul / 160.0, 0.0, 1.0))

        if kurt > DEGRADATION_THRESHOLDS["kurtosis_critical"] or rms > DEGRADATION_THRESHOLDS["rms_critical"]:
            status = "CRITICAL"
            action = "Emergency Stop & Replace"
            priority = 1
        elif kurt > DEGRADATION_THRESHOLDS["kurtosis_warning"] or rms > DEGRADATION_THRESHOLDS["rms_warning"]:
            status = "WARNING"
            action = "Schedule Maintenance (24h)"
            priority = 2
        else:
            status = "HEALTHY"
            action = "Normal Operation"
            priority = 3

        res = dict(asset)
        res.update({
            "health_index": round(hi, 4),
            "status": status,
            "action_required": action,
            "priority": priority
        })
        return res

    def get_plant_health_summary(self) -> Dict[str, Any]:
        """Returns overall plant health score (0-100%), asset rankings, and line summaries."""
        evaluated_assets = [self.compute_asset_status(a) for a in self.assets]
        
        # Sort by priority (1 = highest critical priority)
        evaluated_assets.sort(key=lambda x: (x["priority"], x["health_index"]))

        avg_hi = float(np.mean([a["health_index"] for a in evaluated_assets]))
        plant_health_score = round(avg_hi * 100.0, 1)

        critical_count = sum(1 for a in evaluated_assets if a["status"] == "CRITICAL")
        warning_count = sum(1 for a in evaluated_assets if a["status"] == "WARNING")
        healthy_count = sum(1 for a in evaluated_assets if a["status"] == "HEALTHY")

        return {
            "plant_name": self.plant_name,
            "overall_health_score": plant_health_score,
            "total_assets": len(evaluated_assets),
            "status_breakdown": {
                "critical": critical_count,
                "warning": warning_count,
                "healthy": healthy_count
            },
            "top_critical_asset": evaluated_assets[0]["asset_id"] if critical_count > 0 else "None",
            "fleet_status_table": evaluated_assets
        }

if __name__ == "__main__":
    monitor = PlantFleetMonitor()
    summary = monitor.get_plant_health_summary()
    print(f"=== {summary['plant_name']} Overall Health Score: {summary['overall_health_score']}% ===")
    print(f"Critical: {summary['status_breakdown']['critical']} | Warning: {summary['status_breakdown']['warning']} | Healthy: {summary['status_breakdown']['healthy']}\n")
    print(pd.DataFrame(summary["fleet_status_table"])[["asset_id", "line", "rms", "kurtosis", "health_index", "status", "action_required"]])
