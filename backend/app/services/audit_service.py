"""
SAATHI Audit Logging Service
Persists immutable audit log records for sensitive system operations.
"""

from typing import Optional, Union, Any
import json
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditLog

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        username: str = "system",
        user_role: Optional[str] = None,
        action: str = "ACTION",
        target_resource: str = "resource",
        status: str = "SUCCESS",
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[Union[str, dict, Any]] = None,
        role: Optional[str] = None
    ) -> AuditLog:
        """Creates an immutable audit log entry."""
        effective_role = user_role or role or "UNKNOWN"
        details_str = None
        if details is not None:
            if isinstance(details, (dict, list)):
                details_str = json.dumps(details)
            else:
                details_str = str(details)

        log_entry = AuditLog(
            user_id=user_id,
            username=username,
            user_role=effective_role,
            action=action,
            target_resource=target_resource,
            status=status,
            ip_address=ip_address,
            details=details_str
        )
        db.add(log_entry)
        try:
            db.commit()
        except Exception:
            db.rollback()
        return log_entry
