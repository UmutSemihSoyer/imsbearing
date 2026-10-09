"""
IMS Zero-Gravity Space Station (ISS) Microgravity Lubricant Floating Dynamics Engine
Models bearing wear in zero-g environment where gravity buoyancy is zero and lubricant floats.
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class ZeroGravityISSDynamicsEngine:
    """
    Models zero-gravity fluid dynamics and centrifugal lubricant entrapment for Space Station gyroscopes.
    """

    def evaluate_space_station_bearing(self, rpm: float, gravity_g: float = 0.0) -> Dict[str, Any]:
        """
        Calculates microgravity surface tension lubrication effectiveness.
        """
        # In zero-g, lubricant relies entirely on surface tension capillary forces and centrifugal force
        omega = (rpm / 60.0) * (2.0 * np.pi)
        centrifugal_accel_g = float(((omega**2) * 0.035) / 9.81)

        capillary_retention = "STABLE" if centrifugal_accel_g > 2.0 else "UNSTABLE_LUBRICANT_FLOATING_STARVATION"

        return {
            "environment": "International Space Station (ISS) Microgravity Gyroscope",
            "ambient_gravity_g": gravity_g,
            "rpm": rpm,
            "centrifugal_retention_acceleration_g": round(centrifugal_accel_g, 2),
            "microgravity_lubrication_status": capillary_retention
        }

if __name__ == "__main__":
    iss = ZeroGravityISSDynamicsEngine()
    print(iss.evaluate_space_station_bearing(rpm=2400, gravity_g=0.0))
