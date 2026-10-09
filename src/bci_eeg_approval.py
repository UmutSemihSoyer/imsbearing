"""
IMS Brain-Computer Interface (BCI / EEG) Mental Confirmation Engine
Evaluates operator mental focus (EEG Alpha/Beta ratio) before executing high-risk machine trip commands.
"""

import os
import sys
import numpy as np
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class BCIEEGApprovalEngine:
    """
    Evaluates operator EEG brainwave engagement for mental authorization of emergency commands.
    """

    def verify_operator_bci_focus(self, eeg_alpha_power: float, eeg_beta_power: float) -> Dict[str, Any]:
        """
        Calculates Beta/Alpha ratio (Mental Focus Index). Focus Ratio > 1.5 indicates active confirmation.
        """
        # Beta (13-30 Hz) / Alpha (8-12 Hz) Engagement Ratio
        focus_index = float(eeg_beta_power / (eeg_alpha_power + 1e-6))
        is_confirmed = bool(focus_index >= 1.5)

        return {
            "bci_device": "Neury / OpenBCI 8-Channel Headset",
            "eeg_alpha_power": round(eeg_alpha_power, 2),
            "eeg_beta_power": round(eeg_beta_power, 2),
            "mental_focus_index": round(focus_index, 2),
            "mental_approval_status": "APPROVED_BY_OPERATOR_MENTAL_INTENT" if is_confirmed else "REJECTED_LOW_ATTENTION_LEVEL"
        }

if __name__ == "__main__":
    bci = BCIEEGApprovalEngine()
    print("Active Focus Approval:", bci.verify_operator_bci_focus(eeg_alpha_power=10.2, eeg_beta_power=22.4))
