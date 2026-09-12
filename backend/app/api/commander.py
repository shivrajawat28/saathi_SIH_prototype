"""
SAATHI Commander API Router
Provides non-sensitive administrative endpoints for tracking monthly check-in participation and follow-ups.
Enforces strict psychological privacy: Zero access to individual Support Scores, risk bands, or survey text.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.commander import (
    PendingCheckInsSummary,
    PendingCheckInItem,
    CheckInFollowUpRequest,
    CheckInFollowUpResponse
)
from backend.app.services.commander_service import CommanderService
from backend.app.core.permissions import get_current_user, require_role
from backend.app.core.rate_limit import rate_limit
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/commander", tags=["Commander Administrative Follow-up"])

@router.get(
    "/pending-checkins",
    response_model=PendingCheckInsSummary,
    dependencies=[Depends(require_role("COMMANDER", "ADMIN", "WELFARE_OFFICER"))]
)
def get_pending_monthly_checkins(
    request: Request,
    unit: Optional[str] = Query(None, max_length=64, description="Filter by operational unit"),
    status: Optional[str] = Query(None, max_length=32, description="Filter by status ('PENDING', 'OVERDUE', 'FOLLOW_UP_REQUESTED')"),
    min_days_overdue: Optional[int] = Query(None, ge=0, le=365, description="Filter by minimum days overdue"),
    limit: int = Query(50, ge=1, le=100, description="Pagination item limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List personnel who have not submitted their expected monthly welfare check-in.
    Provides only administrative metadata needed for operational follow-up. Zero private wellness content.
    """
    summary = CommanderService.get_pending_checkins(
        db=db,
        unit_filter=unit,
        status_filter=status,
        min_days_overdue=min_days_overdue,
        limit=limit,
        offset=offset
    )

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.roles[0].name if current_user.roles else "COMMANDER",
        action="VIEW_PENDING_CHECKINS",
        target_resource="commander_followup_panel",
        details={"returned_count": len(summary.items), "total_pending": summary.total_pending},
        ip_address=request.client.host if request.client else None
    )

    return summary


@router.get(
    "/pending-checkins/{personnel_id}",
    response_model=PendingCheckInItem,
    dependencies=[Depends(require_role("COMMANDER", "ADMIN", "WELFARE_OFFICER"))]
)
def get_pending_checkin_detail(
    personnel_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve non-sensitive check-in follow-up details for a specific personnel.
    Guaranteed zero exposure of Support Scores, risk bands, or survey text.
    """
    # Strict validation of personnel_id format
    if not personnel_id.startswith("P-") or len(personnel_id) > 32:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid personnel identifier format.")

    detail = CommanderService.get_personnel_followup_detail(db, personnel_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Personnel '{personnel_id}' not found.")

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.roles[0].name if current_user.roles else "COMMANDER",
        action="VIEW_CHECKIN_FOLLOWUP_DETAIL",
        target_resource=f"personnel:{personnel_id}",
        details={"submission_status": detail.submission_status, "days_overdue": detail.days_overdue},
        ip_address=request.client.host if request.client else None
    )

    return detail


@router.post(
    "/pending-checkins/{personnel_id}/follow-up",
    response_model=CheckInFollowUpResponse,
    dependencies=[Depends(require_role("COMMANDER", "ADMIN")), Depends(rate_limit(max_requests=30, window_seconds=60))]
)
def request_checkin_followup(
    personnel_id: str,
    payload: CheckInFollowUpRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate an administrative follow-up reminder for a pending monthly check-in.
    Creates an immutable audit record and updates follow-up status.
    """
    if not personnel_id.startswith("P-") or len(personnel_id) > 32:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid personnel identifier format.")

    client_ip = request.client.host if request.client else None
    try:
        response = CommanderService.record_follow_up(
            db=db,
            personnel_id=personnel_id,
            commander=current_user,
            notes=payload.notes,
            ip_address=client_ip
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to record check-in follow-up.")
