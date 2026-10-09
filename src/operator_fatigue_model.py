import sys
from typing import Dict, Any

class OperatorFatigueEvaluator:
    """Evaluates technician biometric fatigue and correlates with bearing installation error risk."""
    
    def evaluate_fatigue_and_error_risk(
        self,
        shift_hours_worked: float,
        sleep_hours_last_24h: float,
        reaction_latency_ms: float
    ) -> Dict[str, Any]:
        """
        Calculates Fatigue Index (0.0 to 1.0) and Human Error Assembly Risk Probability.
        """
        # Baseline score calculation
        hours_risk = max(0.0, (shift_hours_worked - 8.0) * 0.1)
        sleep_risk = max(0.0, (7.0 - sleep_hours_last_24h) * 0.12)
        reaction_risk = max(0.0, (reaction_latency_ms - 250.0) / 500.0)
        
        fatigue_index = min(1.0, max(0.0, 0.1 + hours_risk + sleep_risk + reaction_risk))
        
        # Risk assessment for bearing maintenance tasks (e.g. over-tightening, misalignment)
        if fatigue_index < 0.3:
            fitness_status = "FIT_FOR_DUTY"
            assembly_error_prob = 0.02
            action = "Cleared for high-precision bearing alignment."
        elif fatigue_index < 0.65:
            fitness_status = "MODERATE_FATIGUE_WARNING"
            assembly_error_prob = 0.15
            action = "Mandatory 15-min break before critical torque tightening."
        else:
            fitness_status = "UNFIT_HIGH_RISK"
            assembly_error_prob = 0.48
            action = "Reassign technician. High probability of bearing shaft misalignment!"

        return {
            "shift_hours_worked": shift_hours_worked,
            "sleep_hours_last_24h": sleep_hours_last_24h,
            "reaction_latency_ms": reaction_latency_ms,
            "fatigue_index": round(fatigue_index, 3),
            "fitness_status": fitness_status,
            "human_assembly_error_risk_pct": round(assembly_error_prob * 100.0, 1),
            "recommended_action": action
        }

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Stage 64: Operator Fatigue & Human Error Model Test ===")
    evaluator = OperatorFatigueEvaluator()
    
    tech_a = evaluator.evaluate_fatigue_and_error_risk(shift_hours_worked=6.0, sleep_hours_last_24h=7.5, reaction_latency_ms=230.0)
    tech_b = evaluator.evaluate_fatigue_and_error_risk(shift_hours_worked=11.5, sleep_hours_last_24h=4.0, reaction_latency_ms=420.0)
    
    print("Technician A (Rested):", tech_a)
    print("Technician B (Fatigued):", tech_b)
    print("Stage 64 execution complete.")
