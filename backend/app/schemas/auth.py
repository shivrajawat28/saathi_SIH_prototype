"""
SAATHI Authentication & User Pydantic Schemas
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64, description="Username or Service ID")
    password: str = Field(..., min_length=1, max_length=128, description="User password")

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = Field(None, max_length=128)
    role: str = Field(..., description="ADMIN, WELFARE_OFFICER, COMMANDER, ANALYST, PERSONNEL")
    personnel_id: Optional[str] = Field(None, max_length=32)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = {"ADMIN", "WELFARE_OFFICER", "COMMANDER", "ANALYST", "PERSONNEL"}
        if v.upper() not in allowed:
            raise ValueError(f"Invalid role '{v}'. Allowed roles: {allowed}")
        return v.upper()

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    personnel_id: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserProfile(UserResponse):
    permissions: List[str]
