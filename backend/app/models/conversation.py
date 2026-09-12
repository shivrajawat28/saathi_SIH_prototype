"""
SAATHI Voluntary Confidential Wellness Conversation Database Models
Stores structured non-clinical welfare signals extracted from voluntary personnel conversations.
Strictly non-diagnostic: no psychiatric, medical, or clinical labels are stored or inferred.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class WellnessConversation(Base):
    __tablename__ = "wellness_conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(64), unique=True, index=True, nullable=False)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Consent & Privacy
    consent_given = Column(Boolean, default=True, nullable=False)
    consent_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    input_mode = Column(String(32), default="TEXT", nullable=False) # TEXT, VOICE, VOICE_FALLBACK_TEXT

    # Extracted Non-Clinical Welfare Signals
    ai_summary = Column(Text, nullable=False)
    structured_signals = Column(JSON, nullable=False) # JSON dictionary of non-clinical indicators
    confidence = Column(Float, default=0.85, nullable=False)
    urgency_level = Column(String(32), default="NORMAL", nullable=False) # NORMAL, MODERATE, ELEVATED, CRISIS
    is_crisis = Column(Boolean, default=False, nullable=False)
    
    # Signal Integration & Baseline Comparison
    welfare_signal_impact = Column(String(128), nullable=True) # e.g. "Elevated Strain Indicator (+6.5 pts)"
    change_vs_previous = Column(String(256), nullable=True) # e.g. "Fatigue and sleep concerns increased vs last check-in"
    
    # Human Welfare Officer Review
    status = Column(String(32), default="PENDING_REVIEW", nullable=False) # PENDING_REVIEW, ACKNOWLEDGED, INTERVENTION_CREATED
    welfare_officer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(64), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    personnel = relationship("Personnel", back_populates="wellness_conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("wellness_conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    sender = Column(String(16), nullable=False) # USER, ASSISTANT
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_voice = Column(Boolean, default=False, nullable=False)

    conversation = relationship("WellnessConversation", back_populates="messages")
