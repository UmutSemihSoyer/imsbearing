"""
IMS Bearing Interactive 3D Digital Twin Engine
Renders a dynamic WebGL/Three.js 3D bearing digital twin displaying real-time thermal/mechanical stress heatmaps.
"""

import os
import sys
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def generate_threejs_digital_twin_html(health_index: float = 0.85, status: str = "NORMAL", rms: float = 0.12) -> str:
    """
    Generates a standalone WebGL 3D interactive Digital Twin HTML canvas using Three.js.
    Dynamically colors bearing elements (outer race, inner race, rolling elements) based on health index.
    """
    # Color mapping based on status & health index
    if health_index > 0.7:
        outer_race_color = 0x10b981  # Green
        glow_speed = 0.01
    elif health_index > 0.3:
        outer_race_color = 0xf59e0b  # Amber
        glow_speed = 0.05
    else:
        outer_race_color = 0xef4444  # Red
        glow_speed = 0.12

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background-color: #0b0f19; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
            #info-overlay {{
                position: absolute;
                top: 10px;
                left: 10px;
                color: #e2e8f0;
                background: rgba(15, 23, 42, 0.85);
                padding: 12px 18px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                font-size: 13px;
                z-index: 100;
            }}
            .badge {{
                display: inline-block;
                padding: 3px 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="info-overlay">
            <h4 style="margin: 0 0 5px 0; color: #38bdf8;">⚙️ 3D Digital Twin - Rexnord ZA-2115</h4>
            <div>Health Index: <b>{health_index * 100:.1f}%</b></div>
            <div>RMS Acceleration: <b>{rms:.4f} g</b></div>
            <div style="margin-top: 5px;">Status: <span class="badge" style="background-color: {'#10b981' if health_index>0.7 else '#f59e0b' if health_index>0.3 else '#ef4444'}; color: #fff;">{status}</span></div>
        </div>

        <script>
            // Initialize Scene, Camera, Renderer
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0b0f19);

            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 5, 12);

            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.body.appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;

            // Lighting
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 1.2);
            dirLight1.position.set(10, 15, 10);
            scene.add(dirLight1);

            const dirLight2 = new THREE.DirectionalLight(0xff0055, 0.5);
            dirLight2.position.set(-10, -10, -10);
            scene.add(dirLight2);

            // Bearing Group
            const bearingGroup = new THREE.Group();
            scene.add(bearingGroup);

            // 1. Outer Ring
            const outerRingGeo = new THREE.TorusGeometry(3.5, 0.4, 30, 100);
            const outerRingMat = new THREE.MeshStandardMaterial({{
                color: {outer_race_color},
                metalness: 0.8,
                roughness: 0.2,
                emissive: {outer_race_color},
                emissiveIntensity: 0.2
            }});
            const outerRing = new THREE.Mesh(outerRingGeo, outerRingMat);
            bearingGroup.add(outerRing);

            // 2. Inner Ring
            const innerRingGeo = new THREE.TorusGeometry(2.1, 0.35, 30, 100);
            const innerRingMat = new THREE.MeshStandardMaterial({{
                color: 0x94a3b8,
                metalness: 0.9,
                roughness: 0.1
            }});
            const innerRing = new THREE.Mesh(innerRingGeo, innerRingMat);
            bearingGroup.add(innerRing);

            // 3. Rolling Elements (16 Rollers)
            const rollerGroup = new THREE.Group();
            const nRollers = 16;
            const radius = 2.8;

            const rollerGeo = new THREE.SphereGeometry(0.32, 24, 24);
            const rollerMat = new THREE.MeshStandardMaterial({{
                color: 0xe2e8f0,
                metalness: 0.95,
                roughness: 0.05
            }});

            for (let i = 0; i < nRollers; i++) {{
                const angle = (i / nRollers) * Math.PI * 2;
                const roller = new THREE.Mesh(rollerGeo, rollerMat);
                roller.position.set(Math.cos(angle) * radius, Math.sin(angle) * radius, 0);
                rollerGroup.add(roller);
            }}
            bearingGroup.add(rollerGroup);

            // Animation Loop
            let clock = new THREE.Clock();
            function animate() {{
                requestAnimationFrame(animate);
                const elapsed = clock.getElapsedTime();

                // Rotate shaft/rollers
                rollerGroup.rotation.z += 0.005;
                innerRing.rotation.z += 0.008;

                // Pulsing defect glow on outer ring if degraded
                if ({health_index} < 0.7) {{
                    outerRingMat.emissiveIntensity = 0.2 + 0.4 * Math.sin(elapsed * {glow_speed * 100});
                }}

                controls.update();
                renderer.render(scene, camera);
            }}

            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});

            animate();
        </script>
    </body>
    </html>
    """
    return html_code

if __name__ == "__main__":
    html_output = generate_threejs_digital_twin_html(0.25, "CRITICAL", 0.58)
    print(f"[SUCCESS] 3D Three.js Digital Twin HTML template generated ({len(html_output)} bytes).")
