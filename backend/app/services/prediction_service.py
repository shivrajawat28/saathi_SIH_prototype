"""
SAATHI Prediction Service
Coordinates data assembly, baseline computation, ML adapter inference, recommendation generation,
audit logging, and database persistence.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.ml.adapter import ml_adapter
from backend.app.services.recommendation_service import RecommendationService
from backend.app.services.audit_service import AuditService
from backend.app.models.prediction import Prediction, PredictionExplanation, WelfareRecommendation
from backend.app.models.personnel import Personnel
from backend.app.core.config import settings

class PredictionService:
    @staticmethod
    def get_personnel_history(personnel_id: str) -> pd.DataFrame:
        """Loads complete longitudinal history for a given personnel ID."""
        from pathlib import Path
        parquet_candidates = [
            settings.BASE_DIR / "data/processed/integrated_longitudinal.parquet",
            Path.cwd() / "data/processed/integrated_longitudinal.parquet",
            Path(__file__).resolve().parents[3] / "data/processed/integrated_longitudinal.parquet",
        ]
        parquet_path = next((p for p in parquet_candidates if p.exists()), None)
        if parquet_path:
            df = pd.read_parquet(parquet_path)
        else:
            csv_candidates = [
                settings.BASE_DIR / "data/processed/integrated_longitudinal.csv",
                Path.cwd() / "data/processed/integrated_longitudinal.csv",
                Path(__file__).resolve().parents[3] / "data/processed/integrated_longitudinal.csv",
            ]
            csv_path = next((p for p in csv_candidates if p.exists()), None)
            if not csv_path or not csv_path.exists():
                raise FileNotFoundError("Longitudinal dataset not found in data/processed/")
            df = pd.read_csv(csv_path)

        p_records = df[df['personnel_id'] == personnel_id].sort_values('month_idx')
        return p_records

    @classmethod
    def get_latest_longitudinal_observation(cls, personnel_id: str) -> Optional[pd.DataFrame]:
        """
        Loads the integrated longitudinal record for the personnel.
        Uses processed parquet dataset as source of truth.
        """
        p_records = cls.get_personnel_history(personnel_id)
        if len(p_records) == 0:
            return None

        # Return the latest month observation
        return p_records.iloc[[-1]].copy()

    @classmethod
    def generate_personnel_prediction(
        cls,
        db: Session,
        personnel_id: str,
        user_id: Optional[int] = None,
        username: str = "system",
        user_role: Optional[str] = None,
        role: Optional[str] = None,
        ip_address: Optional[str] = None,
        operating_threshold: float = 0.50
    ) -> Dict[str, Any]:
        """
        Executes end-to-end welfare support priority inference.
        """
        effective_role = user_role or role or "WELFARE_OFFICER"
        obs_df = cls.get_latest_longitudinal_observation(personnel_id)
        if obs_df is None:
            AuditService.log_action(
                db, username=username, user_role=effective_role,
                action="RUN_PREDICTION", target_resource=f"personnel:{personnel_id}",
                status="ERROR", user_id=user_id, ip_address=ip_address,
                details="Personnel records not found"
            )
            raise ValueError(f"Personnel ID '{personnel_id}' not found in database or telemetry records.")

        # Run ML inference via locked adapter
        pred_result = ml_adapter.predict_observation(obs_df, operating_threshold=operating_threshold)
        
        # Generate recommendations
        obs_dict = obs_df.iloc[0].to_dict()
        recs = RecommendationService.generate_recommendations(
            priority=pred_result["priority"],
            support_score=pred_result["support_score"] or 0.0,
            top_factors=pred_result["top_factors"],
            observation=obs_dict
        )
        pred_result["recommendations"] = recs

        # Persist to Database if valid personnel exists
        pred_uuid = f"PRED-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        month_idx = int(obs_df['month_idx'].iloc[0]) if 'month_idx' in obs_df.columns else 12

        db_prediction = Prediction(
            prediction_id=pred_uuid,
            personnel_id=personnel_id,
            prediction_month_idx=month_idx,
            support_score=pred_result["support_score"],
            support_priority=pred_result["priority"],
            high_risk_probability=pred_result["high_risk_probability"],
            prediction_reliability=pred_result["prediction_reliability"],
            data_completeness=pred_result["data_completeness"],
            baseline_maturity_months=pred_result["baseline_maturity_months"],
            operating_threshold=operating_threshold,
            human_review_required=pred_result["human_review_required"]
        )
        db.add(db_prediction)

        for factor in pred_result["top_factors"]:
            db_exp = PredictionExplanation(
                prediction_id=pred_uuid,
                factor_name=factor["factor"],
                direction=factor["direction"],
                contribution_score=factor["contribution"]
            )
            db.add(db_exp)

        for rec in recs:
            db_rec = WelfareRecommendation(
                prediction_id=pred_uuid,
                recommendation_type=rec["type"],
                priority_level=rec["priority"],
                reason=rec["reason"]
            )
            db.add(db_rec)

        try:
            db.commit()
        except Exception:
            db.rollback()

        # Audit Log
        AuditService.log_action(
            db, username=username, user_role=effective_role,
            action="RUN_PREDICTION", target_resource=f"personnel:{personnel_id}",
            status="SUCCESS", user_id=user_id, ip_address=ip_address,
            details=f"Generated Priority={pred_result['priority']}, Score={pred_result['support_score']}"
        )

        return pred_result
