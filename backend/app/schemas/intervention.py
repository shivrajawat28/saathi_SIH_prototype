"""
SAATHI Welfare Intervention & Closed-Loop Outcome Schemas
"""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

class InterventionCreate(BaseModel):
    personnel_id: str = Field(..., min_length=3, max_length=32)
    intervention_type: str = Field(..., description="WORKLOAD_REVIEW, RECOVERY_LEAVE, WELFARE_CHECK_IN, COUNSELLING_REFERRAL, SCHEDULE_ADJUSTMENT, FOLLOW_UP_ASSESSMENT")
    action_summary: str = Field(..., min_length=3, max_length=500)
    intervention_date: Optional[date] = None

    @field_validator("intervention_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"WORKLOAD_REVIEW", "RECOVERY_LEAVE", "WELFARE_CHECK_IN", "COUNSELLING_REFERRAL", "SCHEDULE_ADJUSTMENT", "FOLLOW_UP_ASSESSMENT"}
        if v.upper() not in allowed:
            raise ValueError(f"Invalid intervention_type '{v}'. Allowed types: {allowed}")
        return v.upper()

class OutcomeCreate(BaseModel):
    outcome_status: str = Field(..., description="IMPROVED, UNCHANGED, ESCALATED")
    follow_up_notes: str = Field(..., min_length=3, max_length=1000)
    review_date: Optional[date] = None

    @field_validator("outcome_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"IMPROVED", "UNCHANGED", "ESCALATED"}
        if v.upper() not in allowed:
            raise ValueError(f"Invalid outcome_status '{v}'. Allowed values: {allowed}")
        return v.upper()

class OutcomeResponse(BaseModel):
    id: int
    intervention_id: str
    review_date: date
    outcome_status: str
    follow_up_notes: str
    recorded_by_username: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InterventionResponse(BaseModel):
    intervention_id: str
    personnel_id: str
    officer_username: Optional[str] = None
    intervention_type: str
    intervention_date: date
    status: str
    action_summary: str
    created_at: datetime
    outcomes: List[OutcomeResponse] = []

    model_config = ConfigDict(from_attributes=True)
