"""
SAATHI Prediction & Welfare Decision Support API Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
import pandas as pd
from pathlib import Path

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.prediction import Prediction
from backend.app.models.personnel import Personnel, HRProfile
from backend.app.schemas.prediction import PredictionResponse, BatchTriageItem
from backend.app.services.prediction_service import PredictionService
from backend.app.core.permissions import get_current_user, require_role
from backend.app.services.audit_service import AuditService
from backend.app.core.taxonomy import map_department
from backend.app.core.rate_limit import rate_limit
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.post("/personnel/{personnel_id}", response_model=PredictionResponse, dependencies=[Depends(rate_limit(max_requests=60, window_seconds=60))])
def generate_prediction_for_personnel(
    personnel_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate calibrated Welfare Support Priority score and deterministic recommendations
    for an authorized personnel using locked Random Forest and personal historical baseline.
    Restricted to Welfare Officers, Admins, and self-Personnel.
    """
    role = current_user.roles[0].name if current_user.roles else "PERSONNEL"
    
    if role in ["ANALYST", "COMMANDER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Commanders and Analysts access aggregate unit analytics; individual predictions are restricted."
        )

    # Personnel can only query their own score
    if role == "PERSONNEL" and current_user.personnel_id != personnel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Personnel are only permitted to query their own welfare support score."
        )

    client_ip = request.client.host if request.client else None
    try:
        prediction_resp = PredictionService.generate_personnel_prediction(
            db=db,
            personnel_id=personnel_id,
            user_id=current_user.id,
            username=current_user.username,
            role=role,
            ip_address=client_ip
        )
        return prediction_resp
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction computation failure for {personnel_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction service encountered an unexpected error. Please check system audit logs.")

@router.get("/batch-triage", response_model=List[BatchTriageItem], dependencies=[Depends(require_role("WELFARE_OFFICER", "ADMIN"))])
def get_batch_triage(
    department: Optional[str] = None,
    priority_filter: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Batch triage dashboard view for Welfare Officers and Admins to prioritize outreach.
    Returns strictly unique, latest assessment per personnel.
    """
    role = current_user.roles[0].name if current_user.roles else "ADMIN"
    
    # Subquery to identify the latest prediction ID for each personnel_id
    subq = select(
        func.max(Prediction.id).label("max_id")
    ).group_by(Prediction.personnel_id).subquery()

    stmt = select(Prediction).where(Prediction.id.in_(select(subq.c.max_id)))

    if department:
        stmt = stmt.join(Personnel, Personnel.personnel_id == Prediction.personnel_id)\
                   .join(HRProfile, HRProfile.personnel_id == Personnel.personnel_id)\
                   .where(HRProfile.department == department)

    if priority_filter:
        stmt = stmt.where(Prediction.support_priority == priority_filter.upper())

    stmt = stmt.order_by(desc(Prediction.support_score)).limit(limit)
    preds = db.scalars(stmt).all()
    
    seen_personnel = set()
    triage_items: List[BatchTriageItem] = []
    for p in preds:
        if p.personnel_id not in seen_personnel:
            seen_personnel.add(p.personnel_id)
            triage_items.append(BatchTriageItem(
                personnel_id=p.personnel_id,
                support_score=p.support_score or 20.0,
                priority=p.support_priority or "GREEN",
                high_risk_probability=p.high_risk_probability,
                prediction_reliability=p.prediction_reliability or 0.85,
                data_completeness=p.data_completeness or 1.0,
                human_review_required=bool(p.human_review_required),
                predicted_at=p.created_at
            ))

    # If DB has fewer than limit predictions, seed batch triage dynamically from integrated data
    if len(triage_items) == 0:
        data_path = Path(__file__).resolve().parents[3] / "data" / "processed" / "integrated_longitudinal.parquet"
        if data_path.exists():
            df = pd.read_parquet(data_path)
            # Take latest month (12)
            sort_col = "target_support_score_next_month" if "target_support_score_next_month" in df.columns else ("period_latent_strain_score" if "period_latent_strain_score" in df.columns else "workload_score")
            m12 = df[df["month_idx"] == 12].sort_values(sort_col, ascending=False)
            
            if department:
                # Support mapped department query
                if "department" in m12.columns:
                    m12["mapped_dept"] = m12["department"].apply(map_department)
                    m12 = m12[m12["mapped_dept"] == department]

            for _, row in m12.iterrows():
                pid = str(row["personnel_id"])
                if pid in seen_personnel:
                    continue
                prio = str(row.get("period_support_priority", row.get("target_support_priority_next_month", "GREEN")))
                if priority_filter and prio != priority_filter.upper():
                    continue

                score_val = float(row.get(sort_col, 25.0))
                seen_personnel.add(pid)
                triage_items.append(BatchTriageItem(
                    personnel_id=pid,
                    support_score=round(score_val, 1),
                    priority=prio,
                    prediction_reliability=0.88,
                    data_completeness=1.0,
                    human_review_required=(prio in ["ORANGE", "RED"])
                ))
                if len(triage_items) >= limit:
                    break

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        role=role,
        action="VIEW_BATCH_TRIAGE",
        target_resource="triage_dashboard",
        details={"returned_count": len(triage_items)},
        ip_address=request.client.host if request and request.client else None
    )

    return triage_items
