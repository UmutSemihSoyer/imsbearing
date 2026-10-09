"""
IMS WebAR Smart Glass Inspection Overlay Generator
Generates WebXR / AR.js HTML templates for smart glasses (Google Glass, HoloLens) and tablets to overlay 3D health status.
"""

import os
import sys

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def generate_webar_overlay_html(bearing_id: str = "BRG-01", health_index: float = 0.82,
                                 predicted_rul: float = 45.0, status: str = "WARNING") -> str:
    """
    Generates WebAR (AR.js / A-Frame) HTML code for augmented reality smart glasses.
    """
    color_hex = "#10b981" if health_index > 0.7 else ("#f59e0b" if health_index > 0.3 else "#ef4444")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>WebAR Bearing Inspection</title>
        <script src="https://aframe.io/releases/1.2.0/aframe.min.js"></script>
        <script src="https://raw.githack.com/AR-js-org/AR.js/master/aframe/build/aframe-ar.js"></script>
    </head>
    <body style="margin: 0px; overflow: hidden;">
        <a-scene embedded arjs="sourceType: webcam; debugUIEnabled: false;">
            <!-- Hiro AR Marker Target -->
            <a-marker preset="hiro">
                <!-- 3D Holographic Indicator Ring -->
                <a-ring radius-inner="0.8" radius-outer="1.0" color="{color_hex}" rotation="-90 0 0">
                    <a-animation attribute="rotation" to="-90 360 0" dur="4000" repeat="indefinite" easing="linear"></a-animation>
                </a-ring>

                <!-- AR Hologram Info Board -->
                <a-entity position="0 1.2 0" geometry="primitive: plane; width: 2.2; height: 1.2" material="color: #0b0f19; opacity: 0.85">
                    <a-text value="ASSET: {bearing_id}" position="-0.9 0.4 0.01" color="#38bdf8" width="4"></a-text>
                    <a-text value="HEALTH INDEX: {health_index*100:.1f}%" position="-0.9 0.1 0.01" color="{color_hex}" width="3.5"></a-text>
                    <a-text value="PREDICTED RUL: {predicted_rul:.1f} HOURS" position="-0.9 -0.2 0.01" color="#e2e8f0" width="3.5"></a-text>
                    <a-text value="STATUS: {status}" position="-0.9 -0.45 0.01" color="{color_hex}" width="3.5"></a-text>
                </a-entity>
            </a-marker>
            <a-entity camera></a-entity>
        </a-scene>
    </body>
    </html>
    """
    return html_code

if __name__ == "__main__":
    html_str = generate_webar_overlay_html("BRG-LINE1-PUMP1", 0.42, 28.5, "WARNING")
    print(f"[SUCCESS] WebAR Smart Glass HTML template generated ({len(html_str)} bytes).")
