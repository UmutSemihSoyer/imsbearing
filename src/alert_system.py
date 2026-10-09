"""
IMS Bearing Enterprise Alert & Notification System
Handles multi-channel notifications (Telegram, Slack, Email, Webhook) when bearing health degrades to Warning or Critical status.
"""

import time
import os
import sys
import json
import logging
import requests
from typing import Dict, Any, Optional

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import DEGRADATION_THRESHOLDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AlertDispatcher:
    """
    Manages alerting channels (Telegram, Slack, Email, Webhooks) with built-in alert cooldown to prevent notification fatigue.
    """

    def __init__(self, cooldown_seconds: int = 300):
        self.cooldown = cooldown_seconds
        self.last_alert_time: Dict[str, float] = {}

    def _should_suppress(self, alert_key: str) -> bool:
        """Checks if an alert for a specific bearing/channel was sent recently."""
        now = time.time()
        last_time = self.last_alert_time.get(alert_key, 0)
        if (now - last_time) < self.cooldown:
            return True
        self.last_alert_time[alert_key] = now
        return False

    def send_telegram_alert(self, bot_token: str, chat_id: str, message: str) -> bool:
        """Sends an urgent notification to a Telegram Chat / Channel."""
        if not bot_token or not chat_id or bot_token == "YOUR_BOT_TOKEN":
            logging.info(f"[SIMULATED TELEGRAM ALERT]\n{message}")
            return True

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            res = requests.post(url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            logging.error(f"Failed to send Telegram alert: {e}")
            return False

    def send_slack_webhook(self, webhook_url: str, title: str, details: str, severity: str = "warning") -> bool:
        """Sends a rich formatted message card to a Slack channel via Webhook."""
        if not webhook_url or webhook_url == "YOUR_SLACK_WEBHOOK_URL":
            logging.info(f"[SIMULATED SLACK ALERT] {title} | {details}")
            return True

        color = "#FF9900" if severity.lower() == "warning" else "#FF0000"
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 {title}",
                    "text": details,
                    "footer": "IMS Bearing Predictive Maintenance Engine",
                    "ts": int(time.time())
                }
            ]
        }
        try:
            res = requests.post(webhook_url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {e}")
            return False

    def evaluate_and_notify(self, bearing_id: str, features: Dict[str, float], predicted_rul: float,
                            telegram_token: Optional[str] = None, telegram_chat_id: Optional[str] = None,
                            slack_webhook: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluates current vibration telemetry and dispatches alerts if thresholds are breached.
        """
        rms = features.get("rms", 0.0)
        kurtosis = features.get("kurtosis", 0.0)

        severity = "NORMAL"
        if kurtosis > DEGRADATION_THRESHOLDS["kurtosis_critical"] or rms > DEGRADATION_THRESHOLDS["rms_critical"]:
            severity = "CRITICAL"
        elif kurtosis > DEGRADATION_THRESHOLDS["kurtosis_warning"] or rms > DEGRADATION_THRESHOLDS["rms_warning"]:
            severity = "WARNING"

        alert_sent = False
        alert_msg = ""

        if severity in ["WARNING", "CRITICAL"]:
            alert_key = f"{bearing_id}_{severity}"
            if not self._should_suppress(alert_key):
                tag = "[WARNING]" if severity == "WARNING" else "[CRITICAL]"
                title = f"{tag} BEARING FAULT ALERT: {bearing_id}"
                alert_msg = (
                    f"*{title}*\n"
                    f"- Bearing ID: {bearing_id}\n"
                    f"- Status: {severity}\n"
                    f"- RMS Acceleration: {rms:.4f} g\n"
                    f"- Kurtosis: {kurtosis:.2f}\n"
                    f"- Predicted RUL: {predicted_rul:.1f} Hours\n"
                    f"- Recommendation: {'Schedule inspection within 24h' if severity == 'WARNING' else 'STOP MACHINE IMMEDIATELY FOR REPLACEMENT'}"
                )

                # Send notifications across configured channels
                self.send_telegram_alert(telegram_token or "", telegram_chat_id or "", alert_msg)
                self.send_slack_webhook(slack_webhook or "", title, alert_msg, severity)
                alert_sent = True
            else:
                logging.info(f"[ALERT SUPPRESSED] Cooldown active for {alert_key}")


        return {
            "bearing_id": bearing_id,
            "severity": severity,
            "alert_triggered": alert_sent,
            "message": alert_msg
        }

if __name__ == "__main__":
    dispatcher = AlertDispatcher(cooldown_seconds=10)
    
    # Test Normal
    res_norm = dispatcher.evaluate_and_notify("BRG-01", {"rms": 0.08, "kurtosis": 3.1}, 140.0)
    print("Normal Evaluation:", res_norm)

    # Test Warning
    res_warn = dispatcher.evaluate_and_notify("BRG-01", {"rms": 0.28, "kurtosis": 5.2}, 45.0)
    print("Warning Evaluation:", res_warn)

    # Test Critical
    res_crit = dispatcher.evaluate_and_notify("BRG-01", {"rms": 0.65, "kurtosis": 9.4}, 8.2)
    print("Critical Evaluation:", res_crit)
