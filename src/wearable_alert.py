"""
IMS Smartwatch & Wearable Emergency Haptic Alert Engine
Formats and dispatches haptic vibration alerts to Apple Watch, WearOS, and field technician smartwatches.
"""

import os
import sys
import time
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class WearableSmartwatchAlertDispatcher:
    """
    Formats haptic vibration alert payloads for WearOS and Apple Watch.
    """

    HAPTIC_PATTERNS = {
        "WARNING": [200, 100, 200],                  # Double pulse
        "CRITICAL": [500, 100, 500, 100, 500, 100, 800] # SOS Triple heavy pulse
    }

    def format_smartwatch_alert(self, bearing_id: str, severity: str, predicted_rul: float) -> Dict[str, Any]:
        """
        Generates a smartwatch notification payload with custom haptic vibration pattern.
        """
        pattern = self.HAPTIC_PATTERNS.get(severity, [100])

        payload = {
            "notification_id": f"WEAR-{int(time.time())}",
            "device_target": "FIELD_ENGINEER_SMARTWATCH",
            "timestamp": time.strftime("%H:%M:%S", time.localtime()),
            "title": f"ALERT [{severity}]: {bearing_id}",
            "body": f"Bearing RUL = {predicted_rul:.1f} Hours. Immediate inspection required!",
            "haptic_vibration_pattern_ms": pattern,
            "priority": "HIGH" if severity == "CRITICAL" else "MEDIUM",
            "action_buttons": [
                {"id": "ACKNOWLEDGE", "label": "Acknowledge"},
                {"id": "TRIP_MOTOR", "label": "Emergency Trip"}
            ]
        }
        return payload

if __name__ == "__main__":
    wearable = WearableSmartwatchAlertDispatcher()
    crit_alert = wearable.format_smartwatch_alert("PUMP-01-BRG1", "CRITICAL", 4.2)
    print("Smartwatch Critical Haptic Alert Payload:", crit_alert)
