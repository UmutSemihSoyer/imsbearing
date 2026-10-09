import sys
from typing import Dict, Any

class MetaverseVRInspector:
    """Generates WebXR spatial metadata for Meta Quest / Apple Vision Pro factory VR inspection."""
    
    def generate_vr_inspection_overlay(self, bearing_id: str, health_index: float, rul_hours: float) -> Dict[str, Any]:
        """
        Creates spatial HUD overlay coordinates and haptic feedback profiles for WebXR.
        """
        hud_color = "#00FF66" if health_index > 0.7 else ("#FF9900" if health_index > 0.35 else "#FF0033")
        
        spatial_hud = {
            "bearing_id": bearing_id,
            "anchor_position_3d": {"x": 1.25, "y": 1.60, "z": -0.85},
            "hud_billboard": {
                "title": f"BEARING {bearing_id} HEALTH STATUS",
                "health_bar_percent": round(health_index * 100.0, 1),
                "remaining_useful_life_hrs": round(rul_hours, 1),
                "theme_hex_color": hud_color
            },
            "vr_controller_haptic": {
                "frequency_hz": float(np_clip_haptic(health_index)),
                "amplitude": round(1.0 - health_index, 2)
            },
            "supported_headsets": ["Meta Quest 3", "Apple Vision Pro", "HTC Vive XR Elite"]
        }
        return spatial_hud

def np_clip_haptic(hi: float) -> float:
    return max(10.0, min(250.0, (1.0 - hi) * 200.0 + 20.0))

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Stage 71: Metaverse VR Inspection HUD Test ===")
    vr_engine = MetaverseVRInspector()
    hud_data = vr_engine.generate_vr_inspection_overlay("Bearing2_2", health_index=0.28, rul_hours=38.4)
    print("WebXR VR Inspection HUD Profile:", hud_data)
    print("Stage 71 execution complete.")
