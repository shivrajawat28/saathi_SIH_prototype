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
    total_strength: int = Field(..., ge=0, description="Total active personnel count")
    total_submitted_current_month: int = Field(..., ge=0, description="Count of personnel who submitted this month")
    total_pending: int = Field(..., ge=0, description="Count of personnel pending check-in this cycle")
    total_overdue: int = Field(..., ge=0, description="Count of personnel with overdue check-ins")
    total_followup_requested: int = Field(..., ge=0, description="Count of active follow-up requests")
    overdue_count: int = Field(0, ge=0, description="Frontend alias for total_overdue")
    followed_up_count: int = Field(0, ge=0, description="Frontend alias for total_followup_requested")
    current_checkin_cycle: str = Field(..., description="E.g. September 2026")
    cycle_label: str = Field("", description="Frontend alias for current_checkin_cycle")
    cycle_month: str = Field("", description="E.g. 2026-09")
    total: int = Field(..., ge=0, description="Total filtered pending items")
    total_items: int = Field(..., ge=0, description="Frontend alias for total filtered pending items")
    page: int = Field(1, ge=1, description="Active 1-indexed page")
    page_size: int = Field(50, ge=1, description="Page size limit")
    items: List[PendingCheckInItem] = Field(default_factory=list)

class CheckInFollowUpRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=256, description="Optional administrative reminder note")

class CheckInFollowUpResponse(BaseModel):
    status: str = "SUCCESS"
    message: str
    followup_id: int
    personnel_id: str
    target_month: str
    requested_at: datetime
    requested_by_username: Optional[str] = None
    follow_up_status: str

