"""
SAATHI Authentication & Profile API Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.schemas.auth import LoginRequest, Token, UserCreate, UserResponse, UserProfile
from backend.app.models.user import User
from backend.app.services.auth_service import AuthService
from backend.app.core.permissions import get_current_user, require_role, ROLE_PERMISSIONS
from backend.app.core.rate_limit import rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token, dependencies=[Depends(rate_limit(max_requests=60, window_seconds=60))])
def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with username and password, returning a signed JWT access token.
    """
    user = AuthService.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return AuthService.generate_token_for_user(user)

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get profile and effective permissions for the authenticated user.
    """
    role_name = current_user.roles[0].name if current_user.roles else "PERSONNEL"
    perms = list(ROLE_PERMISSIONS.get(role_name, set()))
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=role_name,
        personnel_id=current_user.personnel_id,
        is_active=current_user.is_active,
        permissions=perms
    )

@router.post("/users", response_model=UserResponse, dependencies=[Depends(require_role("ADMIN"))])
def create_user(
    request: Request,
    user_in: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ADMIN only: Register a new system user and assign operational role.
    """
    client_ip = request.client.host if request.client else None
    try:
        new_user = AuthService.create_user(
            db=db,
            user_in=user_in,
            creator_id=current_user.id,
            creator_username=current_user.username,
            ip_address=client_ip
        )
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.roles[0].name if new_user.roles else user_in.role,
            personnel_id=new_user.personnel_id,
            is_active=new_user.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
