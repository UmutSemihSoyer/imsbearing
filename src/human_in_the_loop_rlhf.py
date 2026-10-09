"""
IMS Human-in-the-Loop (RLHF) Feedback Loop
Recalibrates anomaly detection thresholds and RUL predictors based on plant engineer feedback.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import RESULTS_DIR, DEGRADATION_THRESHOLDS

class HumanInTheLoopFeedbackEngine:
    """
    Incorporates expert technician feedback to continuously fine-tune alert sensitivity.
    """

    def __init__(self):
        self.feedback_file = os.path.join(RESULTS_DIR, "human_feedback_log.json")
        self.feedback_history = self._load_history()

    def _load_history(self) -> List[dict]:
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def record_engineer_feedback(self, asset_id: str, feedback_type: str,
                                 engineer_notes: str = "") -> Dict[str, Any]:
        """
        Records human feedback ('FALSE_POSITIVE', 'CORRECT_ALERT', 'RUL_OVERESTIMATED') and updates threshold biases.
        """
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "asset_id": asset_id,
            "feedback_type": feedback_type,
            "engineer_notes": engineer_notes
        }
        self.feedback_history.append(entry)

        os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
        with open(self.feedback_file, "w") as f:
            json.dump(self.feedback_history, f, indent=2)

        # Recalibrate threshold if multiple false positives reported
        fp_count = sum(1 for e in self.feedback_history if e["feedback_type"] == "FALSE_POSITIVE")
        adjusted_kurtosis_threshold = DEGRADATION_THRESHOLDS["kurtosis_warning"] + (fp_count * 0.1)

        print(f"[SUCCESS] Human Feedback Recorded for {asset_id}. Recalibrated Kurtosis Threshold: {adjusted_kurtosis_threshold:.2f}")
        return {
            "entry": entry,
            "total_feedback_count": len(self.feedback_history),
            "recalibrated_kurtosis_warning": round(adjusted_kurtosis_threshold, 2)
        }

if __name__ == "__main__":
    hitl = HumanInTheLoopFeedbackEngine()
    res = hitl.record_engineer_feedback("PUMP-01-BRG1", "FALSE_POSITIVE", "Vibration surge was caused by motor startup, not bearing failure.")
    print("Human Feedback Record Result:", res)
