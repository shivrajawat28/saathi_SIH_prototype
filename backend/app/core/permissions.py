"""
SAATHI Role-Based Access Control (RBAC) & Authorization Module
Enforces role boundaries and provides user retrieval at the API dependency layer.
"""

from typing import List, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.security import decode_access_token
from backend.app.db.session import get_db
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# System Roles
ROLE_ADMIN = "ADMIN"
ROLE_WELFARE_OFFICER = "WELFARE_OFFICER"
ROLE_COMMANDER = "COMMANDER"
ROLE_ANALYST = "ANALYST"
ROLE_PERSONNEL = "PERSONNEL"

ALL_ROLES = [ROLE_ADMIN, ROLE_WELFARE_OFFICER, ROLE_COMMANDER, ROLE_ANALYST, ROLE_PERSONNEL]

ROLE_PERMISSIONS = {
    "ADMIN": {
        "users:manage", "roles:manage", "audit:read", "system:configure",
        "personnel:read", "personnel:write", "predictions:read", "predictions:run",
        "interventions:read", "interventions:write", "analytics:read"
    },
    "WELFARE_OFFICER": {
        "personnel:read", "predictions:read", "predictions:run", "explanations:read",
        "recommendations:read", "interventions:read", "interventions:write",
        "outcomes:write", "simulations:run", "analytics:read"
    },
    "COMMANDER": {
        "personnel:read_summary", "predictions:read_priority", "analytics:read_aggregate",
        "simulations:run"
    },
    "ANALYST": {
        "analytics:read_anonymized", "trends:read"
    },
    "PERSONNEL": {
        "personnel:read_self", "wellness:submit_voluntary", "recommendations:read_self",
        "predictions:read_self", "interventions:read_self"
    }
}

def get_current_user_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """Decodes token and validates signature & expiration."""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def get_current_user(
    payload: dict = Depends(get_current_user_token_payload),
    db: Session = Depends(get_db)
) -> User:
    """Retrieves current authenticated User model instance."""
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token subject.")
    stmt = select(User).where(User.username == username)
    user = db.scalars(stmt).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user account.")
    return user

def require_role(*allowed_roles: Union[str, List[str]]):
    """
    Dependency factory checking whether the authenticated user has an authorized role.
    Supports either positional strings: require_role('ADMIN', 'WELFARE_OFFICER')
    or a list/tuple of strings.
    """
    flat_roles = []
    for r in allowed_roles:
        if isinstance(r, (list, tuple, set)):
            flat_roles.extend(r)
        else:
            flat_roles.append(r)

    def role_checker(payload: dict = Depends(get_current_user_token_payload)) -> dict:
        user_role = payload.get("role")
        if user_role not in flat_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of {flat_roles} roles. Your role is '{user_role}'."
            )
        return payload
    return role_checker
