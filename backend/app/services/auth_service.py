"""
SAATHI Authentication Service
Handles user authentication, password verification, token generation, and account registration.
"""

from typing import Optional, List
from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.user import User, Role
from backend.app.schemas.auth import UserCreate, UserResponse, Token
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.core.config import settings
from backend.app.services.audit_service import AuditService

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        user = db.scalars(stmt).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(
        db: Session,
        user_in: UserCreate,
        creator_id: Optional[int] = None,
        creator_username: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> User:
        # Check existing username
        if db.scalars(select(User).where(User.username == user_in.username)).first():
            raise ValueError(f"Username '{user_in.username}' already registered.")
        if db.scalars(select(User).where(User.email == user_in.email)).first():
            raise ValueError(f"Email '{user_in.email}' already registered.")

        # Resolve role
        role = db.scalars(select(Role).where(Role.name == user_in.role.upper())).first()
        if not role:
            role = Role(name=user_in.role.upper(), description=f"{user_in.role.upper()} role")
            db.add(role)
            db.flush()

        hashed_pw = get_password_hash(user_in.password)
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_pw,
            full_name=user_in.full_name,
            personnel_id=user_in.personnel_id,
            is_active=True
        )
        new_user.roles.append(role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        if creator_id:
            AuditService.log_action(
                db=db,
                user_id=creator_id,
                username=creator_username or "admin",
                role="ADMIN",
                action="CREATE_USER",
                target_resource=f"user:{new_user.username}",
                details={"role": role.name, "personnel_id": user_in.personnel_id},
                ip_address=ip_address
            )

        return new_user

    @staticmethod
    def generate_token_for_user(user: User) -> Token:
        primary_role = user.roles[0].name if user.roles else "PERSONNEL"
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_str = create_access_token(
            subject=user.username,
            role=primary_role,
            expires_delta=access_token_expires
        )
        user_resp = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=primary_role,
            personnel_id=user.personnel_id,
            is_active=user.is_active
        )
        return Token(
            access_token=token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_resp
        )
