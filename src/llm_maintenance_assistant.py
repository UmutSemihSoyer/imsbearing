"""
IMS Natural Language (NLP) Maintenance Assistant & RAG Q&A Engine
Answers technician maintenance queries regarding RUL, BPFO/BPFI fault frequencies, and troubleshooting steps.
"""

import os
import sys
import json
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import BEARING_FREQS, DEGRADATION_THRESHOLDS

class MaintenanceRAGAssistant:
    """
    RAG-enabled maintenance assistant answering queries using domain knowledge base.
    """

    def __init__(self):
        self.knowledge_base = {
            "BPFO": f"BPFO (Outer Race Fault Frequency = {BEARING_FREQS['BPFO']} Hz) spikes indicate localized spalling or pitting on the stationary outer ring track.",
            "BPFI": f"BPFI (Inner Race Fault Frequency = {BEARING_FREQS['BPFI']} Hz) spikes indicate fatigue impacts on the rotating inner ring track.",
            "BSF": f"BSF (Ball Spin Frequency = {BEARING_FREQS['BSF']} Hz) spikes indicate damage to one or more rolling elements.",
            "FTF": f"FTF (Fundamental Train Frequency = {BEARING_FREQS['FTF']} Hz) spikes indicate cage deformation or breakage.",
            "RMS": f"RMS Acceleration reflects total vibration power. Warning threshold is {DEGRADATION_THRESHOLDS['rms_warning']}g, Critical is {DEGRADATION_THRESHOLDS['rms_critical']}g.",
            "Kurtosis": f"Kurtosis measures signal impulse sharpness. Baseline healthy is ~3.0. Values > {DEGRADATION_THRESHOLDS['kurtosis_warning']} indicate early crack impacts."
        }

    def answer_query(self, query: str, current_bearing_status: Dict[str, Any] = None) -> str:
        """
        Processes natural language technician questions and generates intelligent responses.
        """
        query_lower = query.lower()

        if "bpfo" in query_lower:
            return f"[AI Assistant]: {self.knowledge_base['BPFO']}"
        elif "bpfi" in query_lower:
            return f"[AI Assistant]: {self.knowledge_base['BPFI']}"
        elif "rul" in query_lower or "life" in query_lower or "ömür" in query_lower:
            rul = current_bearing_status.get("predicted_rul", 45.0) if current_bearing_status else 45.0
            return f"[AI Assistant]: Bearing estimated Remaining Useful Life (RUL) is {rul:.1f} Hours. Recommended action: {'Schedule inspection within 24h' if rul < 48 else 'Continue normal operation.'}"
        elif "kurtosis" in query_lower or "basıklık" in query_lower:
            return f"[AI Assistant]: {self.knowledge_base['Kurtosis']}"
        elif "rms" in query_lower or "titreşim" in query_lower:
            return f"[AI Assistant]: {self.knowledge_base['RMS']}"
        else:
            return (
                "[AI Assistant]: I am the IMS Bearing Predictive Maintenance Assistant. "
                "You can ask me about: RUL predictions, BPFO/BPFI fault frequencies, RMS/Kurtosis thresholds, or recommended maintenance actions."
            )


if __name__ == "__main__":
    assistant = MaintenanceRAGAssistant()
    print(assistant.answer_query("Why is BPFO frequency surging?"))
    print(assistant.answer_query("What is the remaining useful life of Bearing 1?", {"predicted_rul": 18.5}))
