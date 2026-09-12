"""
SAATHI Deterministic Welfare Recommendation Engine
Generates transparent, rule-based, non-disciplinary supportive action recommendations.
"""

from typing import List, Dict, Any

class RecommendationService:
    @staticmethod
    def generate_recommendations(
        priority: str,
        support_score: float,
        top_factors: List[Dict[str, Any]],
        observation: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generates deterministic decision-support recommendations based on priority and factor triggers.
        """
        recs = []

        # Handle Insufficient Data
        if priority == "INSUFFICIENT_DATA":
            return [{
                "type": "WELFARE_CHECK_IN",
                "priority": "MEDIUM",
                "reason": "Telemetry signals are incomplete. An informal welfare check-in is recommended to verify operational status."
            }]

        factor_names = [f.get("factor", "").lower() for f in top_factors]

        # 1. Recovery Leave Trigger (High leave latency or heavy deployment)
        days_since_leave = observation.get("days_since_prev_leave", 0)
        is_deployed = observation.get("is_deployed", False)
        if days_since_leave >= 100 or "leave" in " ".join(factor_names):
            recs.append({
                "type": "RECOVERY_LEAVE",
                "priority": "HIGH" if priority in ["ORANGE", "RED"] else "MEDIUM",
                "reason": f"Extended period ({int(days_since_leave)} days) since last authorized leave. Consider scheduling recovery rest."
            })

        # 2. Workload & Shift Balancing Trigger
        duty_hrs = observation.get("duty_hours", 0)
        night_shifts = observation.get("night_shifts", 0)
        if duty_hrs >= 210 or night_shifts >= 5 or any("duty" in fn or "night" in fn for fn in factor_names):
            recs.append({
                "type": "WORKLOAD_REVIEW",
                "priority": "HIGH" if priority == "RED" else "MEDIUM",
                "reason": f"Elevated operational tempo ({int(duty_hrs)} monthly duty hrs, {int(night_shifts)} night shifts). Review shift distribution."
            })

        # 3. Schedule Adjustment Trigger
        sched_irreg = observation.get("schedule_irregularity", 1.0)
        if sched_irreg >= 3.0 or any("schedule" in fn or "routine" in fn for fn in factor_names):
            recs.append({
                "type": "SCHEDULE_ADJUSTMENT",
                "priority": "LOW" if priority == "GREEN" else "MEDIUM",
                "reason": "Shift irregularity detected relative to historical pattern. Stabilize shift start times where operationally feasible."
            })

        # 4. Proactive Officer Check-in Trigger (For ORANGE or RED)
        if priority in ["ORANGE", "RED"]:
            recs.append({
                "type": "WELFARE_CHECK_IN",
                "priority": "HIGH",
                "reason": f"Welfare support score ({support_score:.1f}) indicates sustained elevated strain. Authorized welfare officer check-in recommended."
            })

        # 5. Follow-Up Assessment (For RED)
        if priority == "RED":
            recs.append({
                "type": "FOLLOW_UP_ASSESSMENT",
                "priority": "HIGH",
                "reason": "Multi-signal cumulative strain pattern warrants a follow-up review in 14 days to track recovery progress."
            })

        # Fallback for GREEN
        if not recs:
            recs.append({
                "type": "ROUTINE_MONITORING",
                "priority": "LOW",
                "reason": "Occupational rhythm and recovery indicators are within normal personal baseline limits."
            })

        return recs
