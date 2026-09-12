"""
SAATHI What-If Welfare Simulation Service
Simulates potential operational adjustments (e.g., reducing night shifts, granting rest)
and projects model response without modifying permanent personnel history.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

from backend.app.schemas.simulation import SimulationRequest, SimulationResponse, SimulationFactorChange
from backend.app.services.prediction_service import PredictionService
from backend.app.services.recommendation_service import RecommendationService
from backend.app.ml.adapter import ml_adapter
from backend.app.services.audit_service import AuditService

class SimulationService:
    @staticmethod
    def simulate_adjustments(
        db: Session,
        personnel_id: str,
        user_id: int,
        username: str,
        role: str,
        simulation: SimulationRequest,
        ip_address: Optional[str] = None
    ) -> SimulationResponse:
        # 1. Fetch current baseline and recent record
        current_pred = PredictionService.generate_personnel_prediction(
            db=db,
            personnel_id=personnel_id,
            user_id=user_id,
            username=username,
            role=role,
            ip_address=ip_address
        )

        current_score = current_pred.get("support_score") or 25.0
        current_priority = current_pred.get("priority") or "GREEN"

        # 2. Extract recent observation row
        history = PredictionService.get_personnel_history(personnel_id)
        if history.empty:
            raise ValueError(f"Personnel {personnel_id} has no baseline data available for simulation.")

        recent_row = history.iloc[-1:].copy()
        parameter_changes: List[SimulationFactorChange] = []

        # 3. Apply simulated modifications
        if simulation.reduce_night_shifts and "night_shifts" in recent_row.columns:
            before_val = float(recent_row["night_shifts"].iloc[0])
            after_val = max(0.0, before_val - simulation.reduce_night_shifts)
            recent_row["night_shifts"] = after_val
            # Update delta vs baseline if present
            if "night_shifts_personal_mean" in recent_row.columns:
                mean_val = float(recent_row["night_shifts_personal_mean"].iloc[0])
                recent_row["night_shifts_pct_change_vs_baseline"] = ((after_val - mean_val) / max(1.0, mean_val)) * 100.0
            parameter_changes.append(SimulationFactorChange(factor="night_shifts", before=before_val, after=after_val))

        if simulation.reduce_duty_hours and "duty_hours" in recent_row.columns:
            before_val = float(recent_row["duty_hours"].iloc[0])
            after_val = max(0.0, before_val - simulation.reduce_duty_hours)
            recent_row["duty_hours"] = after_val
            if "duty_hours_personal_mean" in recent_row.columns:
                mean_val = float(recent_row["duty_hours_personal_mean"].iloc[0])
                recent_row["duty_hours_pct_change_vs_baseline"] = ((after_val - mean_val) / max(1.0, mean_val)) * 100.0
            parameter_changes.append(SimulationFactorChange(factor="duty_hours", before=before_val, after=after_val))

        if simulation.grant_recovery_days and "days_since_prev_leave" in recent_row.columns:
            before_val = float(recent_row["days_since_prev_leave"].iloc[0])
            after_val = 0.0  # Reset leave latency
            recent_row["days_since_prev_leave"] = after_val
            recent_row["took_leave"] = 1
            parameter_changes.append(SimulationFactorChange(factor="days_since_prev_leave", before=before_val, after=after_val))

        if simulation.reduce_overtime_hours and "overtime_hours" in recent_row.columns:
            before_val = float(recent_row["overtime_hours"].iloc[0])
            after_val = max(0.0, before_val - simulation.reduce_overtime_hours)
            recent_row["overtime_hours"] = after_val
            parameter_changes.append(SimulationFactorChange(factor="overtime_hours", before=before_val, after=after_val))

        # 4. Predict simulated scenario using ml_adapter
        proj_result = ml_adapter.predict_observation(recent_row)
        proj_score = proj_result.get("support_score") or 20.0
        proj_priority = proj_result.get("priority") or "GREEN"

        projected_recs = RecommendationService.generate_recommendations(
            priority=proj_priority,
            support_score=proj_score,
            top_factors=proj_result.get("top_factors", []),
            observation=recent_row.iloc[0].to_dict()
        )

        AuditService.log_action(
            db=db,
            user_id=user_id,
            username=username,
            role=role,
            action="RUN_WHATIF_SIMULATION",
            target_resource=f"personnel:{personnel_id}",
            details={"changes_count": len(parameter_changes), "projected_score": proj_score},
            ip_address=ip_address
        )

        return SimulationResponse(
            personnel_id=personnel_id,
            simulation_only=True,
            current_score=current_score,
            projected_score=proj_score,
            current_priority=current_priority,
            projected_priority=proj_priority,
            projected_delta=round(proj_score - current_score, 2),
            parameter_changes=parameter_changes,
            projected_recommendations=projected_recs
        )
