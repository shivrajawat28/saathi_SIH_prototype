"""
SAATHI Telemetry & Voluntary Wellness Pydantic Schemas
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

class WellnessCheckInRequest(BaseModel):
    sleep_quality: Optional[float] = Field(None, ge=1.0, le=5.0, description="1=Very Poor, 5=Very Good")
    fatigue_level: Optional[float] = Field(None, ge=1.0, le=5.0, description="1=Very Low, 5=Very High")
    work_stress: Optional[float] = Field(None, ge=1.0, le=5.0, description="1=Very Low, 5=Very High")
    mood_wellbeing: Optional[float] = Field(None, ge=1.0, le=5.0, description="1=Very Poor, 5=Very Good")
    work_life_balance: Optional[float] = Field(None, ge=1.0, le=5.0, description="1=Very Poor, 5=Very Good")
    job_satisfaction: Optional[float] = Field(None, ge=1.0, le=5.0, description="1=Very Low, 5=Very High")
    recovery_quality: Optional[float] = Field(None, ge=1.0, le=5.0, description="1=Very Poor, 5=Very Good")
    self_reported_strain: Optional[float] = Field(None, ge=1.0, le=5.0, description="1=Very Low, 5=Very High")

class WellnessCheckInResponse(BaseModel):
    status: str = "SUCCESS"
    message: str = "Voluntary wellness check-in recorded successfully. Data is confidential."

class PersonnelCheckInStatusResponse(BaseModel):
    personnel_id: str
    is_pending: bool
    is_submitted: bool = False
    last_checkin_date: Optional[date] = None
    expected_month: str
    days_overdue: int
    follow_up_requested: bool
    follow_up_status: str = "NONE"
    follow_up_requested_at: Optional[str] = None
    message: str
