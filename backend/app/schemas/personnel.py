"""
SAATHI Personnel Pydantic Schemas
"""

from typing import Optional, List
from datetime import date
from pydantic import BaseModel, ConfigDict

class HRProfileSchema(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    department: Optional[str] = None
    job_role: Optional[str] = None
    job_level: Optional[int] = None
    education_level: Optional[int] = None
    education_field: Optional[str] = None
    marital_status: Optional[str] = None
    distance_from_home: Optional[int] = None
    business_travel: Optional[str] = None
    overtime_eligible: Optional[str] = None
    total_working_years: Optional[int] = None
    years_in_service: Optional[int] = None
    years_in_current_role: Optional[int] = None
    years_since_last_promotion: Optional[int] = None
    years_with_curr_supervisor: Optional[float] = None
    baseline_env_satisfaction: Optional[int] = None
    baseline_job_satisfaction: Optional[int] = None
    baseline_work_life_balance: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class PersonnelSummary(BaseModel):
    personnel_id: str
    department: Optional[str] = None
    job_role: Optional[str] = None
    job_level: Optional[int] = None
    years_in_service: Optional[int] = None
    latest_priority: Optional[str] = None
    latest_support_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class TimelineItem(BaseModel):
    month_idx: int
    date: str
    duty_hours: float
    duty_hours_baseline: Optional[float] = None
    duty_pct_change: Optional[float] = None
    night_shifts: int
    night_shifts_baseline: Optional[float] = None
    night_shifts_pct_change: Optional[float] = None
    rest_hours: float
    workload_score: float
    is_deployed: bool
    deployment_type: Optional[str] = None
    operational_intensity: Optional[int] = None
    took_leave: bool
    leave_type: Optional[str] = None
    days_since_prev_leave: Optional[int] = None
    self_reported_strain: Optional[float] = None
    sleep_quality: Optional[float] = None
    support_score: Optional[float] = None
    support_priority: Optional[str] = None

class PersonnelTimelineResponse(BaseModel):
    personnel_id: str
    total_months: int
    timeline: List[TimelineItem]
