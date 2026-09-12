"""
SAATHI Immutable Audit Log Database Model
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.app.db.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    username = Column(String(64), nullable=False)
    user_role = Column(String(32), nullable=False)
    action = Column(String(64), nullable=False, index=True) # VIEW_PERSONNEL, RUN_PREDICTION, CREATE_INTERVENTION, etc.
    target_resource = Column(String(128), nullable=False, index=True)
    ip_address = Column(String(64), nullable=True)
    status = Column(String(16), nullable=False) # SUCCESS, FORBIDDEN, ERROR
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
