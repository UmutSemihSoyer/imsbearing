"""
IMS Bio-Synthetic Sensor & Enzyme Oil Degradation Engine
Simulates enzymatic bio-receptor reaction rates measuring chemical lubricant oxidation and metal debris.
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class BiosyntheticOilSensorSimulator:
    """
    Simulates bio-enzymatic reaction rate (umol/min) detecting ester oil breakdown and TAN (Total Acid Number).
    """

    def measure_oil_degradation(self, operating_hours: float, temp_c: float) -> Dict[str, Any]:
        """
        Calculates Total Acid Number (TAN mg KOH/g) and bio-enzymatic luminescence.
        """
        tan_index = float(0.05 + (operating_hours / 2000.0)**1.8 * (temp_c / 60.0))
        luminescence_rlu = float(max(10.0, 1000.0 - tan_index * 150.0))

        oil_health = "GOOD" if tan_index < 1.0 else ("DEGRADED" if tan_index < 2.0 else "EXHAUSTED_REPLACE_OIL")

        return {
            "sensor": "Synthetic Enzyme Bio-Receptor Strip",
            "operating_hours": operating_hours,
            "total_acid_number_tan": round(tan_index, 3),
            "bio_luminescence_rlu": round(luminescence_rlu, 1),
            "oil_condition": oil_health
        }

if __name__ == "__main__":
    bio = BiosyntheticOilSensorSimulator()
    print(bio.measure_oil_degradation(operating_hours=1500, temp_c=72.0))
