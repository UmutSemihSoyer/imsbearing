"""
IMS Internationalization (i18n) Multi-Language Translation Engine
Translates UI labels, alerts, and reports into Turkish, English, German, Chinese, and Japanese.
"""

import os
import sys
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class InternationalizationTranslator:
    """
    Manages multi-language dictionary translations for plant operations.
    """

    TRANSLATIONS = {
        "tr": {
            "title": "NASA IMS Rulman Kestirimci Bakım Platformu",
            "health_index": "Sağlık İndeksi (HI)",
            "predicted_rul": "Kalan Faydalı Ömür (RUL)",
            "status_healthy": "Normal Çalışma",
            "status_warning": "Erken Aşınma Uyarısı",
            "status_critical": "Kritik Arıza Seviyesi",
            "recommendation_stop": "MAKANEYİ DERHAL DURDURUN VE RULMANI DEĞİŞTİRİN"
        },
        "en": {
            "title": "NASA IMS Bearing Predictive Maintenance Platform",
            "health_index": "Health Index (HI)",
            "predicted_rul": "Remaining Useful Life (RUL)",
            "status_healthy": "Normal Operation",
            "status_warning": "Early Wearing Warning",
            "status_critical": "Critical Failure Level",
            "recommendation_stop": "STOP MACHINE IMMEDIATELY AND REPLACE BEARING"
        },
        "de": {
            "title": "NASA IMS Lager Vorausschauende Instandhaltung",
            "health_index": "Gesundheitsindex (HI)",
            "predicted_rul": "Restnutzungsdauer (RUL)",
            "status_healthy": "Normaler Betrieb",
            "status_warning": "Warnung vor frühem Verschleiß",
            "status_critical": "Kritischer Fehlerzustand",
            "recommendation_stop": "MASCHINE SOFORT STOPPEN UND LAGER ERSETZEN"
        },
        "zh": {
            "title": "NASA IMS 轴承预测性维护平台",
            "health_index": "健康指数 (HI)",
            "predicted_rul": "剩余使用寿命 (RUL)",
            "status_healthy": "正常运行",
            "status_warning": "早期磨损警告",
            "status_critical": "严重故障级别",
            "recommendation_stop": "立即停止机器并更换轴承"
        },
        "ja": {
            "title": "NASA IMS ベアリング予知保全プラットフォーム",
            "health_index": "健全性指数 (HI)",
            "predicted_rul": "残存有用寿命 (RUL)",
            "status_healthy": "正常運転",
            "status_warning": "早期摩耗警告",
            "status_critical": "重大故障レベル",
            "recommendation_stop": "ただちに機械を停止しベアリングを交換してください"
        }
    }

    def get_text(self, key: str, lang: str = "en") -> str:
        """Retrieves translated text for specified key and language code."""
        lang_dict = self.TRANSLATIONS.get(lang.lower(), self.TRANSLATIONS["en"])
        return lang_dict.get(key, self.TRANSLATIONS["en"].get(key, key))

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    i18n = InternationalizationTranslator()
    print("Turkish:", i18n.get_text("recommendation_stop", "tr"))
    print("English:", i18n.get_text("recommendation_stop", "en"))
    print("German:", i18n.get_text("recommendation_stop", "de"))
    print("Japanese:", i18n.get_text("recommendation_stop", "ja"))

