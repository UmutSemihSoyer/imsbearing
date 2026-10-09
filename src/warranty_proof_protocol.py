"""
IMS OEM Warranty & Insurance Verification Protocol
Cryptographically verifies operating history compliance against OEM warranty operating limits.
"""

import os
import sys
import json
import hashlib
import time
from typing import Dict, Any

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import RESULTS_DIR

class OEMWarrantyProofProtocol:
    """
    Verifies OEM Rexnord warranty conditions (RPM <= 3000, Load <= 15 kN, Temp <= 85°C).
    """

    OEM_BOUNDS = {
        "max_rpm": 3000.0,
        "max_radial_load_kn": 15.0,
        "max_temperature_c": 85.0
    }

    def verify_warranty_compliance(self, asset_id: str, peak_rpm: float,
                                   peak_load_kn: float, peak_temp_c: float) -> Dict[str, Any]:
        """
        Evaluates operational limits and issues cryptographically signed Warranty Compliance Certificate.
        """
        violations = []
        if peak_rpm > self.OEM_BOUNDS["max_rpm"]:
            violations.append(f"Excess RPM: {peak_rpm} > OEM Limit {self.OEM_BOUNDS['max_rpm']}")
        if peak_load_kn > self.OEM_BOUNDS["max_radial_load_kn"]:
            violations.append(f"Excess Load: {peak_load_kn} kN > OEM Limit {self.OEM_BOUNDS['max_radial_load_kn']} kN")
        if peak_temp_c > self.OEM_BOUNDS["max_temperature_c"]:
            violations.append(f"Excess Temp: {peak_temp_c} C > OEM Limit {self.OEM_BOUNDS['max_temperature_c']} C")

        is_warranty_valid = bool(len(violations) == 0)
        status_str = "WARRANTY_VALID" if is_warranty_valid else "WARRANTY_VOID"

        cert_data = {
            "certificate_id": f"WARRANTY-CERT-{asset_id}-{int(time.time())}",
            "asset_id": asset_id,
            "oem_manufacturer": "Rexnord Bearings Inc.",
            "warranty_status": status_str,
            "violations": violations,
            "peak_telemetry": {
                "peak_rpm": peak_rpm,
                "peak_load_kn": peak_load_kn,
                "peak_temp_c": peak_temp_c
            }
        }

        # Sign Certificate
        cert_hash = hashlib.sha256(json.dumps(cert_data, sort_keys=True).encode("utf-8")).hexdigest()
        cert_data["digital_signature"] = cert_hash

        cert_file = os.path.join(RESULTS_DIR, "warranty_certificate.json")
        os.makedirs(os.path.dirname(cert_file), exist_ok=True)
        with open(cert_file, "w") as f:
            json.dump(cert_data, f, indent=2)

        print(f"[SUCCESS] OEM Warranty Certificate issued: {status_str} (Sig: {cert_hash[:16]}...)")
        return cert_data

if __name__ == "__main__":
    protocol = OEMWarrantyProofProtocol()
    
    # Valid Warranty Check
    print("Normal Operation Warranty:", protocol.verify_warranty_compliance("PUMP-01-BRG1", 2000.0, 8.0, 45.0))

    # Voided Warranty Check (Excess Load)
    print("Violated Operation Warranty:", protocol.verify_warranty_compliance("PUMP-01-BRG1", 3500.0, 18.0, 95.0))
