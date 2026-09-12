"""
SAATHI Personnel & Longitudinal Timeline API Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select
import pandas as pd
from pathlib import Path

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.personnel import Personnel, HRProfile
from backend.app.schemas.personnel import PersonnelSummary, HRProfileSchema, PersonnelTimelineResponse, TimelineItem
from backend.app.core.permissions import get_current_user, require_role
from backend.app.services.audit_service import AuditService

from backend.app.core.taxonomy import map_department, map_job_role
from backend.app.models.prediction import Prediction
from sqlalchemy import desc

router = APIRouter(prefix="/personnel", tags=["Personnel"])

INTEGRATED_DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "processed" / "integrated_longitudinal.parquet"

@router.get("/", response_model=List[PersonnelSummary])
def list_personnel(
    request: Request,
    department: Optional[str] = None,
    job_level: Optional[int] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List personnel profiles. Available to ADMIN, WELFARE_OFFICER, COMMANDER.
    Restricted: Analysts and general Personnel cannot perform identity enumeration.
    """
    role = current_user.roles[0].name if current_user.roles else "PERSONNEL"
    if role == "ANALYST":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analysts are restricted to aggregate and anonymized analytics."
        )

    if role == "PERSONNEL":
        if not current_user.personnel_id:
            return []
        p = db.scalars(select(Personnel).where(Personnel.personnel_id == current_user.personnel_id)).first()
        if not p:
            return []
        hr = p.hr_profile
        return [PersonnelSummary(
            personnel_id=p.personnel_id,
            department=map_department(hr.department) if hr else "Operations",
            job_role=map_job_role(hr.job_role) if hr else "Field Personnel",
            job_level=hr.job_level if hr else None,
            years_in_service=hr.years_in_service if hr else None
        )]

    stmt = select(Personnel).join(HRProfile, isouter=True)
    if department:
        stmt = stmt.where(HRProfile.department == department)
    if job_level is not None:
        stmt = stmt.where(HRProfile.job_level == job_level)
    stmt = stmt.offset(offset).limit(limit)

    results = db.scalars(stmt).all()
    summaries = []
    for p in results:
        hr = p.hr_profile
        summaries.append(PersonnelSummary(
            personnel_id=p.personnel_id,
            department=map_department(hr.department) if hr else "Operations",
            job_role=map_job_role(hr.job_role) if hr else "Field Personnel",
            job_level=hr.job_level if hr else None,
            years_in_service=hr.years_in_service if hr else None
        ))

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        role=role,
        action="LIST_PERSONNEL",
        target_resource="personnel_collection",
        details={"count": len(summaries), "offset": offset, "limit": limit},
        ip_address=request.client.host if request.client else None
    )
    return summaries

@router.get("/{personnel_id}", response_model=HRProfileSchema)
def get_personnel_profile(
    personnel_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve baseline HR and occupational profile for a given pseudonymous personnel ID.
    Strict privacy: Individual personnel can only view their own record.
    Commanders and Analysts are restricted to aggregate indicators.
    """
    role = current_user.roles[0].name if current_user.roles else "PERSONNEL"
    if role == "ANALYST":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Analysts are restricted from direct individual identity lookups.")
    if role == "COMMANDER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Commanders view aggregate unit analytics; individual HR profiles are restricted.")
    if role == "PERSONNEL" and current_user.personnel_id != personnel_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Personnel are only permitted to view their own profile.")

    p = db.scalars(select(Personnel).where(Personnel.personnel_id == personnel_id)).first()
    if not p or not p.hr_profile:
        raise HTTPException(status_code=404, detail=f"Personnel {personnel_id} not found.")

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        role=role,
        action="VIEW_PERSONNEL_PROFILE",
        target_resource=f"personnel:{personnel_id}",
        ip_address=request.client.host if request.client else None
    )

    profile_dict = {c.name: getattr(p.hr_profile, c.name) for c in p.hr_profile.__table__.columns}
    profile_dict["department"] = map_department(profile_dict.get("department"))
    profile_dict["job_role"] = map_job_role(profile_dict.get("job_role"))
    return HRProfileSchema(**profile_dict)

@router.get("/{personnel_id}/timeline", response_model=PersonnelTimelineResponse)
def get_personnel_timeline(
    personnel_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve longitudinal occupational timeline and change indicators.
    Restricted to Welfare Officers, Admins, and self-Personnel.
    """
    role = current_user.roles[0].name if current_user.roles else "PERSONNEL"
    if role in ["ANALYST", "COMMANDER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Individual longitudinal timelines are restricted to Welfare Officers and individual personnel."
        )
    if role == "PERSONNEL" and current_user.personnel_id != personnel_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Personnel are only permitted to view their own timeline.")

    if not INTEGRATED_DATA_PATH.exists():
        raise HTTPException(status_code=500, detail="Longitudinal data repository not loaded.")

    df = pd.read_parquet(INTEGRATED_DATA_PATH)
    p_df = df[df["personnel_id"] == personnel_id].sort_values("month_idx")
    if p_df.empty:
        raise HTTPException(status_code=404, detail=f"No longitudinal timeline records found for {personnel_id}.")

    latest_db_pred = db.scalars(
        select(Prediction)
        .where(Prediction.personnel_id == personnel_id)
        .order_by(desc(Prediction.id))
    ).first()

    timeline_items = []
    for _, row in p_df.iterrows():
        # Privacy filter: Hide subjective survey details from Commander to protect psychological safety
        is_commander = (role == "COMMANDER")
        strain = None if is_commander else (float(row["self_reported_strain"]) if pd.notna(row.get("self_reported_strain")) else None)
        sleep = None if is_commander else (float(row["sleep_quality"]) if pd.notna(row.get("sleep_quality")) else None)

        score_val = row.get("support_score")
        prio_val = row.get("support_priority")
        m_idx = int(row["month_idx"])

        if m_idx == 12 and latest_db_pred:
            score_val = latest_db_pred.support_score
            prio_val = latest_db_pred.support_priority
        else:
            if pd.isna(score_val):
                score_val = row.get("target_support_score_next_month", row.get("period_latent_strain_score", 20.0))
            if pd.isna(score_val):
                score_val = 20.0

            if not prio_val or pd.isna(prio_val):
                prio_val = row.get("period_support_priority", row.get("target_support_priority_next_month"))
            if not prio_val or pd.isna(prio_val):
                if float(score_val) >= 80:
                    prio_val = "RED"
                elif float(score_val) >= 55:
                    prio_val = "ORANGE"
                elif float(score_val) >= 30:
                    prio_val = "YELLOW"
                else:
                    prio_val = "GREEN"

        duty_val = row.get("duty_hours")
        if pd.isna(duty_val) or duty_val is None:
            duty_val = row.get("monthly_duty_hours", 160.0)

        duty_base = row.get("duty_hours_personal_mean")
        if pd.isna(duty_base) or duty_base is None:
            duty_base = row.get("duty_hours_baseline")

        duty_pct = row.get("duty_hours_pct_change_vs_baseline")
        if pd.isna(duty_pct) or duty_pct is None:
            duty_pct = row.get("duty_hours_pct_change", 0.0)

        night_base = row.get("night_shifts_personal_mean")
        if pd.isna(night_base) or night_base is None:
            night_base = row.get("night_shifts_baseline")

        night_pct = row.get("night_shifts_pct_change_vs_baseline")
        if pd.isna(night_pct) or night_pct is None:
            night_pct = row.get("night_shifts_pct_change", 0.0)

        wl_val = row.get("workload_score")
        if pd.isna(wl_val) or wl_val is None:
            wl_val = row.get("workload_intensity_score", 50.0)

        timeline_items.append(TimelineItem(
            month_idx=m_idx,
            date=str(row.get("date", f"2025-{m_idx:02d}-01")),
            duty_hours=float(duty_val),
            duty_hours_baseline=float(duty_base) if pd.notna(duty_base) and duty_base is not None else None,
            duty_pct_change=float(duty_pct) if pd.notna(duty_pct) and duty_pct is not None else None,
            night_shifts=int(row.get("night_shifts", 0)),
            night_shifts_baseline=float(night_base) if pd.notna(night_base) and night_base is not None else None,
            night_shifts_pct_change=float(night_pct) if pd.notna(night_pct) and night_pct is not None else None,
            rest_hours=float(row.get("rest_hours", 80.0)),
            workload_score=float(wl_val),
            is_deployed=bool(row.get("is_deployed", False)),
            deployment_type=str(row.get("deployment_type", "None")) if pd.notna(row.get("deployment_type")) else None,
            operational_intensity=int(row.get("operational_intensity", 1)) if pd.notna(row.get("operational_intensity")) else None,
            took_leave=bool(row.get("took_leave", False)),
            leave_type=str(row.get("leave_type", "None")) if pd.notna(row.get("leave_type")) else None,
            days_since_prev_leave=int(row.get("days_since_prev_leave", 30)) if pd.notna(row.get("days_since_prev_leave")) else None,
            self_reported_strain=strain,
            sleep_quality=sleep,
            support_score=round(float(score_val), 1),
            support_priority=str(prio_val)
        ))

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        role=role,
        action="VIEW_PERSONNEL_TIMELINE",
        target_resource=f"personnel:{personnel_id}",
        details={"months_returned": len(timeline_items)},
        ip_address=request.client.host if request.client else None
    )

    return PersonnelTimelineResponse(
        personnel_id=personnel_id,
        total_months=len(timeline_items),
        timeline=timeline_items
    )
