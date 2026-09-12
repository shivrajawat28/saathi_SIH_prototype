"""
SAATHI Commander Monthly Check-In Follow-Up Database Model
Tracks administrative reminder actions initiated by Commanders for pending monthly welfare check-ins.
Strictly non-sensitive: does not record or access private survey responses or AI conversation text.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class CheckInFollowUp(Base):
    __tablename__ = "checkin_followups"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), index=True, nullable=False)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_by_username = Column(String(64), nullable=False)
    target_month = Column(String(16), nullable=False, index=True) # e.g., "2026-09"
    status = Column(String(32), default="FOLLOW_UP_REQUESTED", nullable=False, index=True) # FOLLOW_UP_REQUESTED, COMPLETED, ACKNOWLEDGED
    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    notes = Column(String(256), nullable=True)

    personnel = relationship("Personnel")
    requested_by = relationship("User")
