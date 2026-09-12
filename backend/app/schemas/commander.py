"""
SAATHI Commander Monthly Check-In Follow-Up Schemas
Strictly non-sensitive administrative data models for tracking pending monthly welfare check-in participation.
"""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict

class PendingCheckInItem(BaseModel):
    personnel_id: str = Field(..., min_length=3, max_length=32, description="Pseudonymous personnel identifier")
    display_name: str = Field(..., min_length=1, max_length=64, description="Authorized display name")
    unit: str = Field(..., min_length=1, max_length=64, description="Assigned operational unit")
    role: str = Field(..., min_length=1, max_length=64, description="Occupational role")
    last_checkin_date: Optional[date] = None
    expected_checkin_month: str = Field(..., min_length=3, max_length=32)
    days_overdue: int = Field(..., ge=0, description="Calendar days elapsed past standard check-in window")
    submission_status: str = Field(..., description="'NOT_SUBMITTED', 'PENDING', 'OVERDUE'")
    follow_up_status: str = Field("NONE", description="'NONE', 'FOLLOW_UP_REQUESTED', 'ACKNOWLEDGED', 'COMPLETED'")
    last_followup_at: Optional[datetime] = None
    last_followup_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PendingCheckInsSummary(BaseModel):
    total_strength: int = Field(..., ge=0)
    total_submitted_current_month: int = Field(..., ge=0)
    total_pending: int = Field(..., ge=0)
    total_overdue: int = Field(..., ge=0)
    total_followup_requested: int = Field(..., ge=0)
    current_checkin_cycle: str
    items: List[PendingCheckInItem]

class CheckInFollowUpRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=256, description="Optional administrative reminder note")

class CheckInFollowUpResponse(BaseModel):
    status: str = "SUCCESS"
    message: str
    followup_id: int
    personnel_id: str
    target_month: str
    requested_at: datetime
    follow_up_status: str
