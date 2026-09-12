"""
SAATHI Intervention Service
Manages creation, status tracking, and outcome evaluations for human welfare interventions.
"""

from typing import List, Optional
from datetime import date, datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.intervention import Intervention, InterventionOutcome
from backend.app.schemas.intervention import InterventionCreate, OutcomeCreate
from backend.app.services.audit_service import AuditService

class InterventionService:
    @staticmethod
    def create_intervention(
        db: Session,
        officer_id: int,
        officer_username: str,
        payload: InterventionCreate,
        ip_address: Optional[str] = None
    ) -> Intervention:
        intervention_id = f"INT-{uuid.uuid4().hex[:8].upper()}"
        intervention = Intervention(
            intervention_id=intervention_id,
            personnel_id=payload.personnel_id,
            officer_user_id=officer_id,
            intervention_type=payload.intervention_type,
            intervention_date=payload.intervention_date or date.today(),
            action_summary=payload.action_summary,
            status="OPEN"
        )
        db.add(intervention)
        db.commit()
        db.refresh(intervention)

        AuditService.log_action(
            db=db,
            user_id=officer_id,
            username=officer_username,
            role="WELFARE_OFFICER",
            action="CREATE_INTERVENTION",
            target_resource=f"intervention:{intervention_id}",
            details={"personnel_id": payload.personnel_id, "type": payload.intervention_type},
            ip_address=ip_address
        )
        return intervention

    @staticmethod
    def list_interventions_for_personnel(db: Session, personnel_id: str) -> List[Intervention]:
        stmt = select(Intervention).where(Intervention.personnel_id == personnel_id).order_by(Intervention.intervention_date.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_intervention_by_id(db: Session, intervention_id: str) -> Optional[Intervention]:
        stmt = select(Intervention).where(Intervention.intervention_id == intervention_id)
        return db.scalars(stmt).first()

    @staticmethod
    def record_outcome(
        db: Session,
        intervention_id: str,
        officer_id: int,
        officer_username: str,
        payload: OutcomeCreate,
        ip_address: Optional[str] = None
    ) -> InterventionOutcome:
        intervention = InterventionService.get_intervention_by_id(db, intervention_id)
        if not intervention:
            raise ValueError(f"Intervention {intervention_id} not found")

        outcome = InterventionOutcome(
            intervention_id=intervention_id,
            review_date=payload.review_date or date.today(),
            outcome_status=payload.outcome_status,
            follow_up_notes=payload.follow_up_notes,
            recorded_by_user_id=officer_id
        )
        db.add(outcome)

        # Update parent intervention status
        if payload.outcome_status == "IMPROVED":
            intervention.status = "RESOLVED"
        elif payload.outcome_status == "ESCALATED":
            intervention.status = "ESCALATED"
        else:
            intervention.status = "FOLLOW_UP_REQUIRED"

        db.commit()
        db.refresh(outcome)

        AuditService.log_action(
            db=db,
            user_id=officer_id,
            username=officer_username,
            role="WELFARE_OFFICER",
            action="RECORD_INTERVENTION_OUTCOME",
            target_resource=f"intervention:{intervention_id}",
            details={"outcome_status": payload.outcome_status},
            ip_address=ip_address
        )
        return outcome
