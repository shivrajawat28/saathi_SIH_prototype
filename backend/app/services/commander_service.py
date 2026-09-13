"""
SAATHI Commander Follow-Up Service
Calculates monthly check-in submission status based on calendar cycles and records administrative follow-ups.
Enforces strict privacy: zero access to Support Scores, ML predictions, or voluntary wellness content.
"""

from typing import List, Optional, Tuple
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
import pandas as pd

from backend.app.models.personnel import Personnel, HRProfile
from backend.app.models.telemetry import WellnessRecord
from backend.app.models.conversation import WellnessConversation
from backend.app.models.follow_up import CheckInFollowUp
from backend.app.models.user import User
from backend.app.schemas.commander import (
    PendingCheckInItem,
    PendingCheckInsSummary,
    CheckInFollowUpResponse
)
from backend.app.core.taxonomy import map_department, map_job_role
from backend.app.services.audit_service import AuditService

INTEGRATED_DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "processed" / "integrated_longitudinal.parquet"

class CommanderService:
    @staticmethod
    def get_current_checkin_cycle() -> Tuple[str, date, date]:
        """
        Returns the current monthly check-in cycle name, cycle start date, and standard submission window deadline.
        Example: ('September 2026', 2026-09-01, 2026-09-07)
        """
        today = date.today()
        cycle_name = today.strftime("%B %Y")
        cycle_start = date(today.year, today.month, 1)
        # Check-ins expected within the first 7 days of the month or within 30 days of last check-in
        window_deadline = cycle_start + timedelta(days=7)
        return cycle_name, cycle_start, window_deadline

    @classmethod
    def get_pending_checkins(
        cls,
        db: Session,
        unit_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        follow_up_status: Optional[str] = None,
        search_query: Optional[str] = None,
        min_days_overdue: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
        page: int = 1
    ) -> PendingCheckInsSummary:
        """
        Computes pending monthly check-ins for the active unit strength.
        Identifies personnel who have not submitted their expected monthly check-in.
        """
        today = date.today()
        cycle_name, cycle_start, window_deadline = cls.get_current_checkin_cycle()
        current_month_str = today.strftime("%Y-%m")

        # 1. Fetch all active Personnel with HR Profiles
        stmt = select(Personnel).join(HRProfile, isouter=True)
        all_personnel = db.scalars(stmt).all()

        # 2. Get latest follow-ups mapped by personnel_id
        follow_ups = db.scalars(
            select(CheckInFollowUp)
            .where(CheckInFollowUp.target_month == current_month_str)
            .order_by(desc(CheckInFollowUp.requested_at))
        ).all()
        follow_up_map = {}
        for fu in follow_ups:
            if fu.personnel_id not in follow_up_map:
                follow_up_map[fu.personnel_id] = fu

        # 3. Get latest submitted check-in dates for all personnel from DB
        # Check WellnessRecord (structured survey)
        wellness_records = db.scalars(select(WellnessRecord).order_by(desc(WellnessRecord.date))).all()
        last_wellness_map = {}
        for wr in wellness_records:
            if wr.personnel_id not in last_wellness_map:
                last_wellness_map[wr.personnel_id] = wr.date

        # Check WellnessConversation (AI companion check-in)
        conv_records = db.scalars(select(WellnessConversation).order_by(desc(WellnessConversation.created_at))).all()
        last_conv_map = {}
        for cr in conv_records:
            if cr.personnel_id not in last_conv_map:
                last_conv_map[cr.personnel_id] = cr.created_at.date()

        # Build list of pending items
        total_strength = len(all_personnel)
        total_submitted = 0
        total_pending = 0
        total_overdue = 0
        total_followup_requested = 0

        pending_items: List[PendingCheckInItem] = []

        for p in all_personnel:
            pid = p.personnel_id
            hr = p.hr_profile
            dept_name = map_department(hr.department) if hr and hr.department else "Operations"
            role_name = map_job_role(hr.job_role) if hr and hr.job_role else "Field Personnel"

            # Determine latest check-in date between survey and conversation
            last_w = last_wellness_map.get(pid)
            last_c = last_conv_map.get(pid)
            last_date: Optional[date] = None
            if last_w and last_c:
                last_date = max(last_w, last_c)
            elif last_w:
                last_date = last_w
            elif last_c:
                last_date = last_c

            # Determine if submitted in the current month
            is_submitted_this_month = False
            if last_date and last_date >= cycle_start:
                is_submitted_this_month = True

            fu_record = follow_up_map.get(pid)
            raw_fu_status = fu_record.status if fu_record else "NONE"
            # Normalize status for frontend compatibility
            fu_status = "REQUESTED" if raw_fu_status == "FOLLOW_UP_REQUESTED" else raw_fu_status
            fu_at = fu_record.requested_at if fu_record else None
            fu_by = fu_record.requested_by_username if fu_record else None

            if is_submitted_this_month:
                total_submitted += 1
                if fu_status in ("REQUESTED", "FOLLOW_UP_REQUESTED"):
                    # If follow-up was requested and personnel submitted, mark completed
                    if fu_record:
                        fu_record.status = "COMPLETED"
                        db.add(fu_record)
                        db.commit()
                continue  # Not pending!

            # If not submitted this month, calculate days overdue
            total_pending += 1
            if last_date:
                days_since_last = (today - last_date).days
                days_overdue = max(0, days_since_last - 30)
            else:
                # Never submitted before
                days_overdue = (today - cycle_start).days

            if days_overdue > 0:
                total_overdue += 1
                submission_status = "OVERDUE"
            else:
                submission_status = "PENDING"

            if fu_status in ("REQUESTED", "FOLLOW_UP_REQUESTED"):
                total_followup_requested += 1

            # Apply query filters
            if unit_filter and unit_filter.strip():
                if unit_filter.strip().lower() not in dept_name.lower():
                    continue

            # Search filter (ID, name, department, role)
            if search_query and search_query.strip():
                q = search_query.strip().lower()
                display_str = f"Personnel {pid}".lower()
                if (q not in pid.lower() and 
                    q not in display_str and 
                    q not in dept_name.lower() and 
                    q not in role_name.lower()):
                    continue

            # Follow-up status filter
            effective_fu_filter = follow_up_status or (status_filter if status_filter in ("NONE", "REQUESTED", "FOLLOW_UP_REQUESTED") else None)
            if effective_fu_filter:
                eff_fu = effective_fu_filter.upper()
                if eff_fu == "NONE" and fu_status != "NONE":
                    continue
                elif eff_fu in ("REQUESTED", "FOLLOW_UP_REQUESTED") and fu_status not in ("REQUESTED", "FOLLOW_UP_REQUESTED"):
                    continue

            # Submission status filter
            if status_filter and status_filter.upper() not in ("NONE", "REQUESTED", "FOLLOW_UP_REQUESTED"):
                if status_filter.upper() == "OVERDUE" and submission_status != "OVERDUE":
                    continue
                if status_filter.upper() == "PENDING" and submission_status != "PENDING":
                    continue

            if min_days_overdue is not None and days_overdue < min_days_overdue:
                continue

            pending_items.append(PendingCheckInItem(
                personnel_id=pid,
                display_name=f"Personnel {pid}",
                unit=dept_name,
                role=role_name,
                last_checkin_date=last_date,
                expected_checkin_month=cycle_name,
                days_overdue=days_overdue,
                submission_status=submission_status,
                follow_up_status=fu_status,
                last_followup_at=fu_at,
                last_followup_by=fu_by
            ))

        # Deterministic sorting: Overdue days descending, then personnel_id ascending
        pending_items.sort(key=lambda x: (-x.days_overdue, x.personnel_id))

        total_filtered = len(pending_items)

        # Paginate
        paginated_items = pending_items[offset : offset + limit]

        return PendingCheckInsSummary(
            total_strength=total_strength,
            total_submitted_current_month=total_submitted,
            total_pending=total_pending,
            total_overdue=total_overdue,
            total_followup_requested=total_followup_requested,
            overdue_count=total_overdue,
            followed_up_count=total_followup_requested,
            current_checkin_cycle=cycle_name,
            cycle_label=cycle_name,
            cycle_month=current_month_str,
            total=total_filtered,
            total_items=total_filtered,
            page=page,
            page_size=limit,
            items=paginated_items
        )


    @classmethod
    def get_personnel_followup_detail(
        cls,
        db: Session,
        personnel_id: str
    ) -> Optional[PendingCheckInItem]:
        """
        Retrieves restricted administrative follow-up detail for a single personnel.
        Guaranteed zero leakage of Support Scores, risk bands, or survey answers.
        """
        today = date.today()
        cycle_name, cycle_start, _ = cls.get_current_checkin_cycle()
        current_month_str = today.strftime("%Y-%m")

        p = db.scalars(select(Personnel).where(Personnel.personnel_id == personnel_id)).first()
        if not p:
            return None

        hr = p.hr_profile
        dept_name = map_department(hr.department) if hr and hr.department else "Operations"
        role_name = map_job_role(hr.job_role) if hr and hr.job_role else "Field Personnel"

        # Check latest submissions
        w_rec = db.scalars(select(WellnessRecord).where(WellnessRecord.personnel_id == personnel_id).order_by(desc(WellnessRecord.date))).first()
        c_rec = db.scalars(select(WellnessConversation).where(WellnessConversation.personnel_id == personnel_id).order_by(desc(WellnessConversation.created_at))).first()

        last_date = None
        if w_rec and c_rec:
            last_date = max(w_rec.date, c_rec.created_at.date())
        elif w_rec:
            last_date = w_rec.date
        elif c_rec:
            last_date = c_rec.created_at.date()

        is_submitted_this_month = bool(last_date and last_date >= cycle_start)
        if last_date:
            days_overdue = max(0, (today - last_date).days - 30)
        else:
            days_overdue = (today - cycle_start).days

        submission_status = "SUBMITTED" if is_submitted_this_month else ("OVERDUE" if days_overdue > 0 else "PENDING")

        fu = db.scalars(
            select(CheckInFollowUp)
            .where(CheckInFollowUp.personnel_id == personnel_id, CheckInFollowUp.target_month == current_month_str)
            .order_by(desc(CheckInFollowUp.requested_at))
        ).first()

        pid = p.personnel_id
        return PendingCheckInItem(
            personnel_id=pid,
            display_name=f"Personnel {pid}",
            unit=dept_name,
            role=role_name,
            last_checkin_date=last_date,
            expected_checkin_month=cycle_name,
            days_overdue=days_overdue,
            submission_status=submission_status,
            follow_up_status=fu.status if fu else "NONE",
            last_followup_at=fu.requested_at if fu else None,
            last_followup_by=fu.requested_by_username if fu else None
        )

    @classmethod
    def record_follow_up(
        cls,
        db: Session,
        personnel_id: str,
        commander: User,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> CheckInFollowUpResponse:
        """
        Records a Commander follow-up reminder action.
        """
        today = date.today()
        current_month_str = today.strftime("%Y-%m")

        # Verify personnel exists
        p = db.scalars(select(Personnel).where(Personnel.personnel_id == personnel_id)).first()
        if not p:
            raise ValueError(f"Personnel '{personnel_id}' not found.")

        # Check existing follow-up for this cycle
        existing = db.scalars(
            select(CheckInFollowUp)
            .where(CheckInFollowUp.personnel_id == personnel_id, CheckInFollowUp.target_month == current_month_str)
        ).first()

        if existing:
            existing.status = "FOLLOW_UP_REQUESTED"
            existing.requested_at = datetime.now(timezone.utc)
            existing.requested_by_id = commander.id
            existing.requested_by_username = commander.username
            if notes:
                existing.notes = notes[:256]
            db.add(existing)
            db.commit()
            db.refresh(existing)
            target_fu = existing
        else:
            new_fu = CheckInFollowUp(
                personnel_id=personnel_id,
                requested_by_id=commander.id,
                requested_by_username=commander.username,
                target_month=current_month_str,
                status="FOLLOW_UP_REQUESTED",
                requested_at=datetime.now(timezone.utc),
                notes=notes[:256] if notes else None
            )
            db.add(new_fu)
            db.commit()
            db.refresh(new_fu)
            target_fu = new_fu

        AuditService.log_action(
            db=db,
            user_id=commander.id,
            username=commander.username,
            role="COMMANDER",
            action="REQUEST_CHECKIN_FOLLOWUP",
            target_resource=f"personnel:{personnel_id}",
            details={"target_month": current_month_str, "notes": notes},
            ip_address=ip_address
        )

        return CheckInFollowUpResponse(
            status="SUCCESS",
            message=f"Monthly check-in follow-up request recorded for Personnel {personnel_id}.",
            followup_id=target_fu.id,
            personnel_id=personnel_id,
            target_month=current_month_str,
            requested_at=target_fu.requested_at,
            requested_by_username=commander.username,
            follow_up_status="FOLLOW_UP_REQUESTED"
        )

