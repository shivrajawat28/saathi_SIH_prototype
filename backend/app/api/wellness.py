"""
SAATHI Voluntary Confidential Wellness & AI Conversation Companion API Router
Provides confidential monthly surveys, interactive voluntary AI welfare companion,
speech-to-text processing, and role-restricted Welfare Officer review endpoints.
"""

from typing import Optional, List
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.telemetry import WellnessRecord
from backend.app.models.conversation import WellnessConversation, ConversationMessage
from backend.app.models.follow_up import CheckInFollowUp
from backend.app.schemas.telemetry import (
    WellnessCheckInRequest,
    WellnessCheckInResponse,
    PersonnelCheckInStatusResponse
)
from backend.app.schemas.companion import (
    CompanionChatRequest,
    CompanionChatResponse,
    CompanionSubmitRequest,
    CompanionConversationSummaryResponse,
    CompanionReviewRequest,
    VoiceTranscribeRequest,
    VoiceTranscribeResponse,
    CompanionChatMessage
)
from backend.app.core.permissions import get_current_user, require_role
from backend.app.services.audit_service import AuditService
from backend.app.services.companion_service import CompanionService

router = APIRouter(prefix="/wellness", tags=["Wellness & Companion"])


@router.get("/check-in-status", response_model=PersonnelCheckInStatusResponse)
def get_personnel_checkin_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the monthly check-in submission status for the authenticated personnel.
    """
    target_pid = current_user.personnel_id or "P-000013"
    today = date.today()
    cycle_name = today.strftime("%B %Y")
    cycle_start = date(today.year, today.month, 1)
    current_month_str = today.strftime("%Y-%m")

    # Check latest survey and companion submission
    w_rec = db.scalars(select(WellnessRecord).where(WellnessRecord.personnel_id == target_pid).order_by(desc(WellnessRecord.date))).first()
    c_rec = db.scalars(select(WellnessConversation).where(WellnessConversation.personnel_id == target_pid).order_by(desc(WellnessConversation.created_at))).first()

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

    is_pending = not is_submitted_this_month

    fu = db.scalars(
        select(CheckInFollowUp)
        .where(CheckInFollowUp.personnel_id == target_pid, CheckInFollowUp.target_month == current_month_str)
        .order_by(desc(CheckInFollowUp.requested_at))
    ).first()

    follow_up_req = bool(fu and fu.status == "FOLLOW_UP_REQUESTED")
    follow_up_at = fu.requested_at.isoformat() if (fu and fu.requested_at) else None

    if not is_pending:
        msg = f"Your monthly welfare check-in for {cycle_name} has been submitted. Thank you for your voluntary participation."
    elif follow_up_req:
        msg = f"Your monthly check-in for {cycle_name} is pending ({days_overdue} days overdue). A reminder has been requested by your unit commander."
    else:
        msg = f"Your monthly check-in for {cycle_name} is due. Please take a few moments to complete your voluntary check-in."

    return PersonnelCheckInStatusResponse(
        personnel_id=target_pid,
        is_pending=is_pending,
        is_submitted=is_submitted_this_month,
        last_checkin_date=last_date,
        expected_month=cycle_name,
        days_overdue=days_overdue if is_pending else 0,
        follow_up_requested=follow_up_req,
        follow_up_status=fu.status if fu else "NONE",
        follow_up_requested_at=follow_up_at,
        message=msg
    )


# =====================================================================
# 1. TRADITIONAL VOLUNTARY SURVEY CHECK-IN
# =====================================================================

@router.post("/check-in", response_model=WellnessCheckInResponse)
def submit_voluntary_check_in(
    request: Request,
    check_in: WellnessCheckInRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Voluntary personnel monthly wellness survey check-in submission.
    Strictly confidential: Answers are restricted and never shared with commanders as raw surveys.
    """
    if not current_user.personnel_id:
        # Fallback for admin or unassociated users in demo
        target_pid = "P-000013"
    else:
        target_pid = current_user.personnel_id

    rec = WellnessRecord(
        personnel_id=target_pid,
        month_idx=12,
        date=date.today(),
        sleep_quality=check_in.sleep_quality,
        fatigue_level=check_in.fatigue_level,
        work_stress=check_in.work_stress,
        mood_wellbeing=check_in.mood_wellbeing,
        work_life_balance=check_in.work_life_balance,
        job_satisfaction=check_in.job_satisfaction,
        recovery_quality=check_in.recovery_quality,
        self_reported_strain=check_in.self_reported_strain,
        checkin_completion=True
    )
    db.add(rec)

    # Mark active follow-up as COMPLETED
    current_month_str = date.today().strftime("%Y-%m")
    fu = db.scalars(
        select(CheckInFollowUp)
        .where(CheckInFollowUp.personnel_id == target_pid, CheckInFollowUp.target_month == current_month_str)
    ).first()
    if fu and fu.status == "FOLLOW_UP_REQUESTED":
        fu.status = "COMPLETED"
        db.add(fu)

    db.commit()

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.roles[0].name if current_user.roles else "PERSONNEL",
        action="SUBMIT_VOLUNTARY_WELLNESS",
        target_resource=f"personnel:{target_pid}",
        details={"is_voluntary": True},
        ip_address=request.client.host if request.client else None
    )

    return WellnessCheckInResponse(
        status="SUCCESS",
        message="Voluntary wellness check-in recorded successfully. Data is confidential."
    )


# =====================================================================
# 2. VOLUNTARY AI WELFARE COMPANION INTERACTIVE CHAT
# =====================================================================

@router.post("/companion/chat", response_model=CompanionChatResponse)
def chat_with_companion(
    request: Request,
    payload: CompanionChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Interactive turn with SAATHI Voluntary AI Wellness Companion.
    Provides empathetic, non-diagnostic response and extracts structured non-clinical welfare signals.
    """
    if not payload.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voluntary participation consent is required to process conversation."
        )

    personnel_id = current_user.personnel_id or "P-000013"
    response = CompanionService.process_chat_turn(
        db=db,
        personnel_id=personnel_id,
        request=payload,
        current_user=current_user
    )
    return response


@router.post("/companion/voice-transcribe", response_model=VoiceTranscribeResponse)
def transcribe_voice(
    payload: VoiceTranscribeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Speech-to-text transcription service with graceful fallback.
    Does not perform facial or biometric surveillance.
    """
    return CompanionService.transcribe_audio(payload)


@router.post("/companion/submit", response_model=CompanionConversationSummaryResponse)
def submit_companion_session(
    request: Request,
    payload: CompanionSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit completed voluntary conversation session for authorized Welfare Officer review.
    Stores structured signals, AI non-clinical summary, and minimal metadata.
    """
    if not payload.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voluntary consent must be given to submit welfare conversation for review."
        )

    personnel_id = current_user.personnel_id or "P-000013"
    client_ip = request.client.host if request.client else None

    conv = CompanionService.submit_conversation_session(
        db=db,
        personnel_id=personnel_id,
        current_user=current_user,
        consent_given=payload.consent_given,
        input_mode=payload.input_mode,
        messages=payload.messages,
        ip_address=client_ip
    )

    # Mark active follow-up as COMPLETED
    current_month_str = datetime.now(timezone.utc).strftime("%Y-%m")
    fu = db.scalars(
        select(CheckInFollowUp)
        .where(CheckInFollowUp.personnel_id == personnel_id, CheckInFollowUp.target_month == current_month_str)
    ).first()
    if fu and fu.status == "FOLLOW_UP_REQUESTED":
        fu.status = "COMPLETED"
        db.add(fu)
        db.commit()

    msg_schemas = [
        CompanionChatMessage(
            sender=m.sender,
            text=m.text,
            timestamp=m.timestamp,
            is_voice=m.is_voice
        ) for m in conv.messages
    ]

    return CompanionConversationSummaryResponse(
        id=conv.id,
        conversation_id=conv.conversation_id,
        personnel_id=conv.personnel_id,
        created_at=conv.created_at,
        consent_given=conv.consent_given,
        input_mode=conv.input_mode,
        ai_summary=conv.ai_summary,
        structured_signals=conv.structured_signals,
        confidence=conv.confidence,
        urgency_level=conv.urgency_level,
        is_crisis=conv.is_crisis,
        welfare_signal_impact=conv.welfare_signal_impact,
        change_vs_previous=conv.change_vs_previous,
        status=conv.status,
        welfare_officer_notes=conv.welfare_officer_notes,
        reviewed_by=conv.reviewed_by,
        reviewed_at=conv.reviewed_at,
        messages=msg_schemas
    )


# =====================================================================
# 3. PERSONNEL SELF-SERVICE CONVERSATION HISTORY
# =====================================================================

@router.get("/companion/history", response_model=List[CompanionConversationSummaryResponse])
def get_my_conversation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve current authenticated personnel's own past voluntary check-in sessions.
    """
    personnel_id = current_user.personnel_id or "P-000013"
    convs = db.scalars(
        select(WellnessConversation)
        .where(WellnessConversation.personnel_id == personnel_id)
        .order_by(desc(WellnessConversation.created_at))
    ).all()

    result = []
    for c in convs:
        result.append(CompanionConversationSummaryResponse(
            id=c.id,
            conversation_id=c.conversation_id,
            personnel_id=c.personnel_id,
            created_at=c.created_at,
            consent_given=c.consent_given,
            input_mode=c.input_mode,
            ai_summary=c.ai_summary,
            structured_signals=c.structured_signals,
            confidence=c.confidence,
            urgency_level=c.urgency_level,
            is_crisis=c.is_crisis,
            welfare_signal_impact=c.welfare_signal_impact,
            change_vs_previous=c.change_vs_previous,
            status=c.status,
            welfare_officer_notes=c.welfare_officer_notes,
            reviewed_by=c.reviewed_by,
            reviewed_at=c.reviewed_at
        ))
    return result


# =====================================================================
# 4. WELFARE OFFICER RESTRICTED CONVERSATION REVIEW
# =====================================================================

@router.get("/companion/personnel/{personnel_id}", response_model=List[CompanionConversationSummaryResponse])
def get_personnel_conversation_signals(
    personnel_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve structured voluntary conversation summaries and signals for Welfare Officer review.
    STRICT PRIVACY: Blocked for Commanders and Analysts (returns 403 Forbidden).
    """
    role = current_user.roles[0].name if current_user.roles else "PERSONNEL"

    if role in ["COMMANDER", "ANALYST"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Commanders and Analysts are strictly restricted from viewing individual voluntary conversation details."
        )

    if role == "PERSONNEL" and current_user.personnel_id != personnel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Personnel are only permitted to view their own conversation records."
        )

    convs = db.scalars(
        select(WellnessConversation)
        .where(WellnessConversation.personnel_id == personnel_id)
        .order_by(desc(WellnessConversation.created_at))
    ).all()

    # If no records exist in DB for demo candidate, seed a realistic voluntary conversation for P-000013
    if len(convs) == 0 and personnel_id == "P-000013":
        demo_signals = {
            "sleep_difficulty": "Elevated",
            "fatigue": "Elevated",
            "workload_pressure": "Elevated",
            "emotional_exhaustion": "Moderate",
            "recovery_difficulty": "Elevated",
            "personal_concern": "Reported (Homesickness/Family)",
            "morale_concern": "None",
            "social_withdrawal": False,
            "positive_resilience_indicators": [
                "Operational dedication and readiness affirmed",
                "Supportive peer rapport maintained"
            ],
            "sentiment_valence": "Strained",
            "urgency_level": "MODERATE",
            "extraction_confidence": 0.88,
            "primary_strain_driver": "Fatigue, Sleep disruption, Recovery gap"
        }
        demo_conv = WellnessConversation(
            conversation_id=f"CONV-DEMO-P13",
            personnel_id=personnel_id,
            created_at=datetime.now(timezone.utc),
            consent_given=True,
            consent_timestamp=datetime.now(timezone.utc),
            input_mode="VOICE_FALLBACK_TEXT",
            ai_summary="Personnel voluntarily shared concerns regarding persistent fatigue, poor sleep after continuous night duties, and leave latency. Positive peer support affirmed.",
            structured_signals=demo_signals,
            confidence=0.88,
            urgency_level="MODERATE",
            is_crisis=False,
            welfare_signal_impact="Elevated Strain Signal (+6.5 pts supplementary welfare weight)",
            change_vs_previous="Self-reported fatigue and sleep concerns have increased compared with previous baseline.",
            status="PENDING_REVIEW"
        )
        db.add(demo_conv)
        db.commit()
        db.refresh(demo_conv)
        convs = [demo_conv]

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        role=role,
        action="VIEW_CONVERSATION_SIGNALS",
        target_resource=f"personnel:{personnel_id}",
        details={"records_returned": len(convs)},
        ip_address=request.client.host if request.client else None
    )

    result = []
    for c in convs:
        result.append(CompanionConversationSummaryResponse(
            id=c.id,
            conversation_id=c.conversation_id,
            personnel_id=c.personnel_id,
            created_at=c.created_at,
            consent_given=c.consent_given,
            input_mode=c.input_mode,
            ai_summary=c.ai_summary,
            structured_signals=c.structured_signals,
            confidence=c.confidence,
            urgency_level=c.urgency_level,
            is_crisis=c.is_crisis,
            welfare_signal_impact=c.welfare_signal_impact,
            change_vs_previous=c.change_vs_previous,
            status=c.status,
            welfare_officer_notes=c.welfare_officer_notes,
            reviewed_by=c.reviewed_by,
            reviewed_at=c.reviewed_at
        ))
    return result


@router.post("/companion/{conversation_id}/review", response_model=CompanionConversationSummaryResponse)
def review_companion_conversation(
    conversation_id: str,
    review_req: CompanionReviewRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Welfare Officer action endpoint to acknowledge voluntary check-in, record officer notes,
    and initiate proactive welfare interventions.
    """
    role = current_user.roles[0].name if current_user.roles else "PERSONNEL"
    if role not in ["WELFARE_OFFICER", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authorized Welfare Officers and Admins can record review actions."
        )

    conv = db.scalars(
        select(WellnessConversation)
        .where(WellnessConversation.conversation_id == conversation_id)
    ).first()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation record not found.")

    conv.status = review_req.status
    if review_req.notes:
        conv.welfare_officer_notes = review_req.notes
    conv.reviewed_by = current_user.username
    conv.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(conv)

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        username=current_user.username,
        role=role,
        action="REVIEW_CONVERSATION_SIGNALS",
        target_resource=f"conversation:{conversation_id}",
        details={"status": review_req.status, "notes": review_req.notes},
        ip_address=request.client.host if request.client else None
    )

    return CompanionConversationSummaryResponse(
        id=conv.id,
        conversation_id=conv.conversation_id,
        personnel_id=conv.personnel_id,
        created_at=conv.created_at,
        consent_given=conv.consent_given,
        input_mode=conv.input_mode,
        ai_summary=conv.ai_summary,
        structured_signals=conv.structured_signals,
        confidence=conv.confidence,
        urgency_level=conv.urgency_level,
        is_crisis=conv.is_crisis,
        welfare_signal_impact=conv.welfare_signal_impact,
        change_vs_previous=conv.change_vs_previous,
        status=conv.status,
        welfare_officer_notes=conv.welfare_officer_notes,
        reviewed_by=conv.reviewed_by,
        reviewed_at=conv.reviewed_at
    )
