"""
IMS Cost & Risk Optimizer
Calculates the optimal financial maintenance window balancing planned replacement costs vs catastrophic downtime risks.
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class CostRiskOptimizer:
    """
    Optimizes maintenance replacement timing using Weibull failure probability curves and financial cost matrices.
    """

    def __init__(self, planned_cost_usd: float = 2500.0, unplanned_downtime_cost_usd: float = 150000.0):
        self.c_planned = planned_cost_usd
        self.c_unplanned = unplanned_downtime_cost_usd

    def calculate_optimal_maintenance_window(self, predicted_rul_hours: float, beta_shape: float = 3.5) -> Dict[str, Any]:
        """
        Finds the exact hour t* that minimizes total expected financial risk.
        """
        time_steps = np.arange(0, int(predicted_rul_hours * 2.0) + 1, 1)
        
        # Weibull Cumulative Failure Probability P(t)
        eta_scale = max(1.0, predicted_rul_hours / (np.log(2) ** (1.0 / beta_shape)))
        p_failure = 1.0 - np.exp(- (time_steps / eta_scale) ** beta_shape)

        # Expected Cost C(t) = C_planned * (1 - P(t)) + (C_planned + C_unplanned) * P(t)
        expected_costs = (self.c_planned * (1.0 - p_failure)) + ((self.c_planned + self.c_unplanned) * p_failure)

        optimal_idx = np.argmin(expected_costs)
        optimal_hour = float(time_steps[optimal_idx])
        min_expected_cost = float(expected_costs[optimal_idx])

        return {
            "predicted_rul_hours": predicted_rul_hours,
            "optimal_maintenance_hour": optimal_hour,
            "minimum_expected_cost_usd": round(min_expected_cost, 2),
            "planned_cost_usd": self.c_planned,
            "unplanned_catastrophic_risk_usd": self.c_unplanned,
            "risk_mitigation_savings_usd": round(self.c_unplanned - min_expected_cost, 2)
        }

if __name__ == "__main__":
    optimizer = CostRiskOptimizer(planned_cost_usd=2500.0, unplanned_downtime_cost_usd=150000.0)
    result = optimizer.calculate_optimal_maintenance_window(predicted_rul_hours=36.0)
    print("Financial Risk Optimization:", result)
