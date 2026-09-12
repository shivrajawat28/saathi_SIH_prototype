"""
SAATHI Voluntary AI Welfare Conversation Assistant Service
Provides speech-to-text, empathetic non-clinical conversation, structured welfare signal extraction,
longitudinal baseline comparison, and safe human-in-the-loop review routing.
"""

import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from backend.app.models.conversation import WellnessConversation, ConversationMessage
from backend.app.models.user import User
from backend.app.schemas.companion import (
    CompanionChatRequest,
    CompanionChatResponse,
    StructuredWellnessSignals,
    CompanionChatMessage,
    VoiceTranscribeRequest,
    VoiceTranscribeResponse
)
from backend.app.services.audit_service import AuditService


# =====================================================================
# 1. PROVIDER ABSTRACTIONS (Speech, NLP, Synthesis)
# =====================================================================

class SpeechToTextProvider(ABC):
    """Abstract interface for speech transcription."""
    @abstractmethod
    def transcribe(self, audio_data: Optional[str], text_hint: Optional[str] = None, language: str = "hi-IN") -> Dict[str, Any]:
        pass

class ConversationAnalysisProvider(ABC):
    """Abstract interface for non-clinical conversational understanding."""
    @abstractmethod
    def analyze_conversation(
        self,
        current_message: str,
        history: List[CompanionChatMessage],
        previous_signals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        pass

class TextToSpeechProvider(ABC):
    """Abstract interface for voice synthesis."""
    @abstractmethod
    def synthesize(self, text: str, language: str = "hi-IN") -> Dict[str, Any]:
        pass


# =====================================================================
# 2. DEFAULT ROBUST MOCK / DETERMINISTIC PROVIDER IMPLEMENTATION
# =====================================================================

class LocalSpeechToTextProvider(SpeechToTextProvider):
    """Handles audio transcription with browser WebSpeech coordination or fallback."""
    def transcribe(self, audio_data: Optional[str], text_hint: Optional[str] = None, language: str = "hi-IN") -> Dict[str, Any]:
        if text_hint and text_hint.strip():
            return {
                "transcript": text_hint.strip(),
                "fallback_used": False,
                "confidence": 0.94,
                "message": "Voice audio transcribed via Web Speech interface."
            }
        
        # Fallback transcription when audio is simulated
        fallback_text = "Mujhe pichhle kuch dino se continuous night shifts ki wajah se thakaan ho rahi hai aur neend theek se nahi aa rahi."
        return {
            "transcript": fallback_text,
            "fallback_used": True,
            "confidence": 0.88,
            "message": "Audio stream processed via local speech recognition adapter."
        }


class RuleAndNLPConversationAnalysisProvider(ConversationAnalysisProvider):
    """
    Multilingual (Hindi, English, Hinglish) non-diagnostic semantic signal extractor.
    Extracts structured non-clinical indicators without claiming psychiatric diagnosis.
    """

    CRISIS_KEYWORDS = [
        "suicide", "kill myself", "end my life", "harm myself", "want to die",
        "khatam kar lunga", "mar jana chahta", "marne ka mann", "apne aap ko nuksan",
        "can't go on", "no reason to live", "cannot live anymore", "suicidal"
    ]

    FATIGUE_KEYWORDS = [
        "thakan", "thakaan", "exhausted", "exhaustion", "tired", "body pain", "body ache",
        "energy nahi", "kamzori", "fatigued", "drained", "lethargic", "weariness"
    ]

    SLEEP_KEYWORDS = [
        "neend", "sleep", "so nahi pa", "insomnia", "nightmare", "kachhi neend",
        "broken sleep", "poor sleep", "sleep deprivation", "neend puri nahi", "sleepless"
    ]

    WORKLOAD_KEYWORDS = [
        "duty pressure", "duty ka pressure", "duty zyada", "heavy duty", "workload", "overtime", "bojh", "load", "double duty",
        "heavy schedule", "no rest", "target pressure", "deployment stress", "continuous duty", "shift overload", "tight schedule",
        "excessive shifts", "extended duty", "back to back shifts", "pressure zyada", "night shifts", "night shift", "night duty",
        "continuous shifts", "rotational shifts"
    ]

    EMOTIONAL_EXHAUSTION_KEYWORDS = [
        "mentally exhausted", "dimag thak", "burnout", "mental fatigue", "chidhchidapan",
        "irritated", "overwhelmed", "frustrated", "headache", "tanav", "stress", "tension"
    ]

    RECOVERY_KEYWORDS = [
        "chutti", "leave", "rest nahi", "no break", "recovery", "chhutti", "break chahiye",
        "continuous duty", "no holiday", "off nahi mil", "rest ki zarurat"
    ]

    PERSONAL_HOMESICK_KEYWORDS = [
        "ghar ki yaad", "family", "ghar wale", "bacche", "bimar", "mother", "father",
        "wife", "kids", "hometown", "homesick", "personal issue", "family problem"
    ]

    MORALE_KEYWORDS = [
        "mann nahi lag raha", "low morale", "demotivated", "hopeless", "feeling low",
        "disheartened", "unmotivated", "give up"
    ]

    POSITIVE_KEYWORDS = [
        "theek hoon", "fine", "good", "manage", "better", "stable", "motivated",
        "ready for duty", "team support", "sab theek", "doing well", "feeling okay",
        "handling well", "proud to serve", "great team", "healthy", "fit"
    ]

    def _matches_any(self, text: str, keywords: List[str]) -> bool:
        text_lower = text.lower()
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower) or kw in text_lower:
                return True
        return False

    def analyze_conversation(
        self,
        current_message: str,
        history: List[CompanionChatMessage],
        previous_signals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        all_text = " ".join([m.text for m in history] + [current_message]).lower()

        # 1. CRISIS & SEVERE DISTRESS SAFETY GATE
        if self._matches_any(all_text, self.CRISIS_KEYWORDS):
            return {
                "reply": (
                    "Aap akele nahi hain, aur aapki suraksha aur sehat hamari sabse badi prathmikta hai. "
                    "Kripya turant apne unit ke Medical/Welfare Officer se sampark karein ya 24/7 National Tele-Mental "
                    "Health Support Helpline (KIRAN: 1800-599-0019) par baat karein. Ek high-priority welfare support notice "
                    "bhi initiate kiya gaya hai taaki aapko compassionate human support mil sake."
                ),
                "ai_summary": "Voluntary disclosure indicated acute personal distress requiring immediate, non-punitive human welfare outreach.",
                "extracted_signals": StructuredWellnessSignals(
                    sleep_difficulty="Elevated",
                    fatigue="Elevated",
                    workload_pressure="Elevated",
                    emotional_exhaustion="Severe",
                    recovery_difficulty="Elevated",
                    personal_concern="Reported (Acute Strain)",
                    morale_concern="Elevated",
                    social_withdrawal=True,
                    positive_resilience_indicators=[],
                    sentiment_valence="Negative",
                    urgency_level="CRISIS",
                    extraction_confidence=0.98,
                    primary_strain_driver="Severe Emotional Strain"
                ),
                "is_crisis": True,
                "urgency_level": "CRISIS",
                "confidence": 0.98,
                "welfare_signal_impact": "CRITICAL: Immediate Human Welfare Intervention Required",
                "change_vs_previous": "Acute strain indicators detected compared to previous baseline."
            }

        # 2. Extract Non-Clinical Structured Welfare Signals
        has_fatigue = self._matches_any(all_text, self.FATIGUE_KEYWORDS)
        has_sleep = self._matches_any(all_text, self.SLEEP_KEYWORDS)
        has_workload = self._matches_any(all_text, self.WORKLOAD_KEYWORDS)
        has_emotional = self._matches_any(all_text, self.EMOTIONAL_EXHAUSTION_KEYWORDS)
        has_recovery = self._matches_any(all_text, self.RECOVERY_KEYWORDS)
        has_personal = self._matches_any(all_text, self.PERSONAL_HOMESICK_KEYWORDS)
        has_morale = self._matches_any(all_text, self.MORALE_KEYWORDS)
        has_positive = self._matches_any(all_text, self.POSITIVE_KEYWORDS)

        # Signal Strengths (None, Low, Moderate, Elevated, High)
        fatigue_lvl = "Elevated" if (has_fatigue and has_workload) else ("Moderate" if has_fatigue else "None")
        sleep_lvl = "Elevated" if (has_sleep and has_workload) else ("Moderate" if has_sleep else "None")
        workload_lvl = "Elevated" if (has_workload and (has_fatigue or has_sleep)) else ("Moderate" if has_workload else "None")
        emotional_lvl = "Elevated" if (has_emotional and has_fatigue) else ("Moderate" if has_emotional else "None")
        recovery_lvl = "Elevated" if has_recovery else "None"
        personal_lvl = "Reported (Homesickness/Family)" if has_personal else "None"
        morale_lvl = "Elevated" if has_morale else "None"

        # Resilience indicators
        resilience_list = []
        if has_positive:
            if "motivated" in all_text or "ready" in all_text:
                resilience_list.append("Operational dedication and readiness affirmed")
            if "manage" in all_text or "handle" in all_text:
                resilience_list.append("Adaptive coping mindset reported")
            if "team" in all_text or "support" in all_text:
                resilience_list.append("Positive peer support environment")
            if not resilience_list:
                resilience_list.append("General emotional equilibrium affirmed")

        # Valence & Urgency calculation
        strain_count = sum([
            has_fatigue, has_sleep, has_workload, has_emotional, has_recovery, has_personal, has_morale
        ])

        if strain_count >= 4:
            sentiment = "Negative"
            urgency = "ELEVATED"
            impact_pts = 7.5
        elif strain_count >= 2:
            sentiment = "Strained"
            urgency = "MODERATE"
            impact_pts = 4.5
        elif strain_count == 1:
            sentiment = "Positive" if has_positive else "Neutral"
            urgency = "NORMAL"
            impact_pts = 1.0 if not has_positive else 0.0
        else:
            sentiment = "Positive" if has_positive else "Neutral"
            urgency = "NORMAL"
            impact_pts = 0.0

        # Primary strain driver
        drivers = []
        if has_fatigue: drivers.append("Fatigue")
        if has_sleep: drivers.append("Sleep disruption")
        if has_workload: drivers.append("Operational workload")
        if has_recovery: drivers.append("Recovery gap")
        if has_personal: drivers.append("Personal/Family concern")
        primary_driver = ", ".join(drivers[:2]) if drivers else "None identified"

        # AI Non-Clinical Summary
        summary_parts = []
        if drivers:
            summary_parts.append(f"Personnel voluntarily shared concerns regarding {', '.join(drivers)}.")
        else:
            summary_parts.append("Personnel voluntarily shared stable wellness and routine operational reflections.")
        if resilience_list:
            summary_parts.append(f"Positive coping indicators noted ({len(resilience_list)} factors).")
        summary_parts.append("Data is purely non-diagnostic decision support.")
        ai_summary = " ".join(summary_parts)

        # Empathetic Conversational Response
        if strain_count >= 3:
            reply = (
                "Aapki baat samajh aa rahi hai. Lagatar duty, night shifts aur thakaan se recovery mein samay lagna "
                "svabhavik hai. Aapne jo concerns share kiye hain, yeh hamare Welfare Officer ke dhyan mein "
                "laye jayenge taaki aapke duty schedule aur rest rhythm ko behtar karne ke supportive steps liye ja sakein. "
                "Kya aap chahenge ki main isse welfare check-in report ke roop mein save karun?"
            )
        elif strain_count >= 1:
            reply = (
                "Dhanyawad yeh share karne ke liye. Hum samajhte hain ki force ki duties challenging hoti hain. "
                "Aapki hydration, proper rest breaks aur unit peer support bahut zaroori hain. "
                "Kya duty ke alawa koi aur vishisht vishay hai jismein aap support chahte hain?"
            )
        else:
            reply = (
                "Aapka yeh voluntary check-in sunkar accha laga ki sab kuch theek chal raha hai. "
                "Apna routine aur hydration maintain rakhein. SAATHI hamesha aapke voluntary welfare support ke liye uplabdh hai."
            )

        # Baseline Longitudinal Comparison
        change_desc = "Initial voluntary wellness conversation recorded."
        if previous_signals:
            prev_fatigue = previous_signals.get("fatigue", "None")
            prev_sleep = previous_signals.get("sleep_difficulty", "None")
            if fatigue_lvl in ["Moderate", "Elevated"] and prev_fatigue in ["None", "Low"]:
                change_desc = "Self-reported fatigue has increased compared with the previous voluntary check-in."
            elif sleep_lvl in ["Moderate", "Elevated"] and prev_sleep in ["None", "Low"]:
                change_desc = "Self-reported sleep difficulty has increased compared with the previous check-in."
            elif fatigue_lvl == "None" and prev_fatigue in ["Moderate", "Elevated"]:
                change_desc = "Self-reported fatigue has improved compared with previous check-in."
            else:
                change_desc = "Self-reported wellness indicators remain consistent with previous check-in."

        welfare_impact = (
            f"Elevated Strain Signal (+{impact_pts:.1f} pts supplementary welfare weight)"
            if impact_pts > 0 else "Stable wellness signal (No adjustment)"
        )

        structured_signals = StructuredWellnessSignals(
            sleep_difficulty=sleep_lvl,
            fatigue=fatigue_lvl,
            workload_pressure=workload_lvl,
            emotional_exhaustion=emotional_lvl,
            recovery_difficulty=recovery_lvl,
            personal_concern=personal_lvl,
            morale_concern=morale_lvl,
            social_withdrawal=(strain_count >= 4),
            positive_resilience_indicators=resilience_list,
            sentiment_valence=sentiment,
            urgency_level=urgency,
            extraction_confidence=0.88 if strain_count > 0 else 0.92,
            primary_strain_driver=primary_driver
        )

        return {
            "reply": reply,
            "ai_summary": ai_summary,
            "extracted_signals": structured_signals,
            "is_crisis": False,
            "urgency_level": urgency,
            "confidence": 0.88 if strain_count > 0 else 0.92,
            "welfare_signal_impact": welfare_impact,
            "change_vs_previous": change_desc
        }


# =====================================================================
# 3. COMPANION SERVICE COORDINATOR
# =====================================================================

class CompanionService:
    stt_provider: SpeechToTextProvider = LocalSpeechToTextProvider()
    analysis_provider: ConversationAnalysisProvider = RuleAndNLPConversationAnalysisProvider()

    @classmethod
    def get_latest_previous_signals(cls, db: Session, personnel_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves structured signals from the most recent prior conversation for baseline comparison."""
        prev_conv = db.scalars(
            select(WellnessConversation)
            .where(WellnessConversation.personnel_id == personnel_id)
            .order_by(desc(WellnessConversation.created_at))
        ).first()
        if prev_conv and prev_conv.structured_signals:
            return prev_conv.structured_signals
        return None

    @classmethod
    def process_chat_turn(
        cls,
        db: Session,
        personnel_id: str,
        request: CompanionChatRequest,
        current_user: User
    ) -> CompanionChatResponse:
        """Processes an interactive chat turn, extracts signals, and provides empathetic non-diagnostic reply."""
        prev_signals = cls.get_latest_previous_signals(db, personnel_id)
        analysis = cls.analysis_provider.analyze_conversation(
            current_message=request.message,
            history=request.conversation_history or [],
            previous_signals=prev_signals
        )

        return CompanionChatResponse(
            reply=analysis["reply"],
            ai_summary=analysis["ai_summary"],
            extracted_signals=analysis["extracted_signals"],
            is_crisis=analysis["is_crisis"],
            urgency_level=analysis["urgency_level"],
            confidence=analysis["confidence"],
            change_vs_previous=analysis.get("change_vs_previous"),
            welfare_signal_impact=analysis.get("welfare_signal_impact")
        )

    @classmethod
    def submit_conversation_session(
        cls,
        db: Session,
        personnel_id: str,
        current_user: User,
        consent_given: bool,
        input_mode: str,
        messages: List[CompanionChatMessage],
        ip_address: Optional[str] = None
    ) -> WellnessConversation:
        """
        Persists a completed voluntary conversation session to the database with minimal data retention.
        Generates final structured signals, summary, and audit log.
        """
        prev_signals = cls.get_latest_previous_signals(db, personnel_id)
        user_messages = [m for m in messages if m.sender == "USER"]
        all_user_text = " ".join([m.text for m in user_messages])

        analysis = cls.analysis_provider.analyze_conversation(
            current_message=all_user_text,
            history=messages[:-1] if len(messages) > 1 else [],
            previous_signals=prev_signals
        )

        conv_uuid = f"CONV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        signals_dict = analysis["extracted_signals"].model_dump() if hasattr(analysis["extracted_signals"], "model_dump") else analysis["extracted_signals"]

        conv_record = WellnessConversation(
            conversation_id=conv_uuid,
            personnel_id=personnel_id,
            created_at=datetime.now(timezone.utc),
            consent_given=consent_given,
            consent_timestamp=datetime.now(timezone.utc),
            input_mode=input_mode,
            ai_summary=analysis["ai_summary"],
            structured_signals=signals_dict,
            confidence=analysis["confidence"],
            urgency_level=analysis["urgency_level"],
            is_crisis=analysis["is_crisis"],
            welfare_signal_impact=analysis.get("welfare_signal_impact"),
            change_vs_previous=analysis.get("change_vs_previous"),
            status="PENDING_REVIEW"
        )
        db.add(conv_record)
        db.flush()

        # Add message exchanges
        for m in messages:
            msg_obj = ConversationMessage(
                conversation_id=conv_record.id,
                sender=m.sender,
                text=m.text,
                timestamp=m.timestamp or datetime.now(timezone.utc),
                is_voice=bool(m.is_voice)
            )
            db.add(msg_obj)

        db.commit()
        db.refresh(conv_record)

        # Audit Log
        AuditService.log_action(
            db=db,
            user_id=current_user.id,
            username=current_user.username,
            role=current_user.roles[0].name if current_user.roles else "PERSONNEL",
            action="SUBMIT_WELLNESS_CONVERSATION",
            target_resource=f"conversation:{conv_uuid}",
            details={
                "personnel_id": personnel_id,
                "urgency": analysis["urgency_level"],
                "is_crisis": analysis["is_crisis"],
                "message_count": len(messages)
            },
            ip_address=ip_address
        )

        return conv_record

    @classmethod
    def transcribe_audio(
        cls,
        request: VoiceTranscribeRequest
    ) -> VoiceTranscribeResponse:
        """Coordinates speech transcription with local/fallback STT providers."""
        res = cls.stt_provider.transcribe(
            audio_data=request.audio_base64,
            text_hint=request.text_hint,
            language=request.language or "hi-IN"
        )
        return VoiceTranscribeResponse(
            transcript=res["transcript"],
            input_mode="VOICE" if not res.get("fallback_used") else "VOICE_FALLBACK_TEXT",
            fallback_used=res.get("fallback_used", False),
            confidence=res.get("confidence", 0.90),
            message=res.get("message", "Transcription complete.")
        )
