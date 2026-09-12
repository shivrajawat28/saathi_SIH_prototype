"""
SAATHI Welfare Intervention & Closed-Loop Tracking API Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.intervention import (
    InterventionCreate,
    InterventionResponse,
    OutcomeCreate,
    OutcomeResponse
)
from backend.app.services.intervention_service import InterventionService
from backend.app.core.permissions import get_current_user, require_role

router = APIRouter(prefix="/interventions", tags=["Interventions"])

@router.post("/", response_model=InterventionResponse, dependencies=[Depends(require_role("WELFARE_OFFICER", "ADMIN"))])
def create_welfare_intervention(
    request: Request,
    payload: InterventionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Authorized Welfare Officer action: Record a proactive welfare intervention (e.g. Workload Review, Rest Leave).
    """
    client_ip = request.client.host if request.client else None
    try:
        intervention = InterventionService.create_intervention(
            db=db,
            officer_id=current_user.id,
            officer_username=current_user.username,
            payload=payload,
            ip_address=client_ip
        )
        return InterventionResponse(
            intervention_id=intervention.intervention_id,
            personnel_id=intervention.personnel_id,
            officer_username=current_user.username,
            intervention_type=intervention.intervention_type,
            intervention_date=intervention.intervention_date,
            status=intervention.status,
            action_summary=intervention.action_summary,
            created_at=intervention.created_at,
            outcomes=[]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/personnel/{personnel_id}", response_model=List[InterventionResponse])
def get_personnel_interventions(
    personnel_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List recorded interventions and follow-up outcomes for a personnel.
    """
    role = current_user.roles[0].name if current_user.roles else "PERSONNEL"
    if role in ["ANALYST", "COMMANDER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Individual intervention records are restricted to Welfare Officers, Admins, and self-Personnel."
        )
    if role == "PERSONNEL" and current_user.personnel_id != personnel_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Personnel can only view interventions intended for themselves.")

    interventions = InterventionService.list_interventions_for_personnel(db, personnel_id)
    results = []
    for item in interventions:
        outcomes_list = [
            OutcomeResponse(
                id=o.id,
                intervention_id=o.intervention_id,
                review_date=o.review_date,
                outcome_status=o.outcome_status,
                follow_up_notes=o.follow_up_notes,
                recorded_by_username=o.recorded_by.username if o.recorded_by else None,
                created_at=o.created_at
            ) for o in item.outcomes
        ]
        results.append(InterventionResponse(
            intervention_id=item.intervention_id,
            personnel_id=item.personnel_id,
            officer_username=item.officer.username if item.officer else None,
            intervention_type=item.intervention_type,
            intervention_date=item.intervention_date,
            status=item.status,
            action_summary=item.action_summary,
            created_at=item.created_at,
            outcomes=outcomes_list
        ))
    return results

@router.post("/{intervention_id}/outcomes", response_model=OutcomeResponse, dependencies=[Depends(require_role("WELFARE_OFFICER", "ADMIN"))])
def record_intervention_outcome(
    intervention_id: str,
    request: Request,
    payload: OutcomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record longitudinal outcome evaluation (IMPROVED, UNCHANGED, ESCALATED) for a closed-loop intervention.
    """
    client_ip = request.client.host if request.client else None
    try:
        outcome = InterventionService.record_outcome(
            db=db,
            intervention_id=intervention_id,
            officer_id=current_user.id,
            officer_username=current_user.username,
            payload=payload,
            ip_address=client_ip
        )
        return OutcomeResponse(
            id=outcome.id,
            intervention_id=outcome.intervention_id,
            review_date=outcome.review_date,
            outcome_status=outcome.outcome_status,
            follow_up_notes=outcome.follow_up_notes,
            recorded_by_username=current_user.username,
            created_at=outcome.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to record intervention outcome. Please check system audit logs.")
