import sys
from typing import Dict, Any

class SyntheticDNASentinelsMonitor:
    """Engineered bio-protein sentinels dissolved in synthetic lubricant for molecular shear/heat sensing."""
    
    def evaluate_protein_denaturation(self, oil_temp_c: float, shear_rate_sec: float) -> Dict[str, Any]:
        """
        Evaluates synthetic protein sentinel conformational state.
        Green GFP = Pristine, Yellow YFP = Thermal Stress, Red RFP = Severe Shear Breakdown.
        """
        thermal_denaturation_pct = min(100.0, max(0.0, (oil_temp_c - 60.0) * 1.5))
        shear_breakdown_pct = min(100.0, max(0.0, (shear_rate_sec - 10000.0) / 500.0))
        
        total_degradation = min(100.0, thermal_denaturation_pct + shear_breakdown_pct)
        
        if total_degradation < 25.0:
            fluorescence = "EMERALD_GREEN_GFP (Pristine Lubricant)"
            status = "HEALTHY"
        elif total_degradation < 65.0:
            fluorescence = "AMBER_YELLOW_YFP (Thermal Stress Threshold Reached)"
            status = "WARNING"
        else:
            fluorescence = "CRIMSON_RED_RFP (Severe Shear & Molecular Breakdown)"
            status = "CRITICAL_OIL_REPLACEMENT_NEEDED"

        return {
            "oil_temp_c": oil_temp_c,
            "shear_rate_sec": shear_rate_sec,
            "synthetic_dna_sentinel_status": status,
            "fluorescence_color_code": fluorescence,
            "denatured_protein_percentage": round(total_degradation, 1)
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Stage 87: Synthetic Bio-DNA Sentinel Lubricant Test ===")
    sentinel_mon = SyntheticDNASentinelsMonitor()
    
    normal_bio = sentinel_mon.evaluate_protein_denaturation(oil_temp_c=55.0, shear_rate_sec=5000.0)
    degraded_bio = sentinel_mon.evaluate_protein_denaturation(oil_temp_c=105.0, shear_rate_sec=25000.0)
    
    print("Normal Bio-Sentinel State:", normal_bio)
    print("Degraded Bio-Sentinel State:", degraded_bio)
    print("Stage 87 execution complete.")
