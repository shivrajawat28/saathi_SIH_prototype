"""
SAATHI Security & Compliance Audit Log API Router
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from pydantic import BaseModel, ConfigDict

from backend.app.db.session import get_db
from backend.app.models.audit import AuditLog
from backend.app.core.permissions import require_role

router = APIRouter(prefix="/audit", tags=["Audit & Security"])

class AuditLogEntry(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: str
    user_role: str
    action: str
    target_resource: str
    status: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

@router.get("/logs", response_model=List[AuditLogEntry], dependencies=[Depends(require_role("ADMIN"))])
def get_audit_logs(
    action: Optional[str] = None,
    username: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    ADMIN only: Inspect chronological immutable security and access audit logs.
    """
    stmt = select(AuditLog).order_by(desc(AuditLog.timestamp))
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if username:
        stmt = stmt.where(AuditLog.username == username)
    stmt = stmt.offset(offset).limit(limit)

    logs = db.scalars(stmt).all()
    return logs
