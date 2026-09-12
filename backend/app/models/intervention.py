"""
SAATHI Welfare Intervention & Closed-Loop Outcome Models
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    intervention_id = Column(String(64), unique=True, index=True, nullable=False)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), index=True, nullable=False)
    officer_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    intervention_type = Column(String(64), nullable=False) # WORKLOAD_REVIEW, RECOVERY_LEAVE, etc.
    intervention_date = Column(Date, nullable=False)
    status = Column(String(32), default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, CLOSED
    action_summary = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    personnel = relationship("Personnel", back_populates="interventions")
    officer = relationship("User", foreign_keys=[officer_user_id])
    outcomes = relationship("InterventionOutcome", back_populates="intervention", cascade="all, delete-orphan")

class InterventionOutcome(Base):
    __tablename__ = "intervention_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    intervention_id = Column(String(64), ForeignKey("interventions.intervention_id", ondelete="CASCADE"), index=True, nullable=False)
    review_date = Column(Date, nullable=False)
    outcome_status = Column(String(32), nullable=False) # IMPROVED, UNCHANGED, ESCALATED
    follow_up_notes = Column(Text, nullable=False)
    recorded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    intervention = relationship("Intervention", back_populates="outcomes")
    recorded_by = relationship("User", foreign_keys=[recorded_by_user_id])
