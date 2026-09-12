"""
SAATHI What-If Welfare Scenario Simulation Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SimulationRequest(BaseModel):
    reduce_night_shifts: Optional[int] = Field(0, ge=0, le=30, description="Hypothetical reduction in monthly night shifts")
    reduce_duty_hours: Optional[float] = Field(0.0, ge=0.0, le=200.0, description="Hypothetical reduction in monthly duty hours")
    grant_recovery_days: Optional[int] = Field(0, ge=0, le=30, description="Hypothetical authorized recovery leave days")
    reduce_overtime_hours: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Hypothetical overtime reduction")

class SimulationFactorChange(BaseModel):
    factor: str
    before: Any
    after: Any

class SimulationResponse(BaseModel):
    personnel_id: str
    simulation_only: bool = True
    current_score: float
    projected_score: float
    current_priority: str
    projected_priority: str
    projected_delta: float
    parameter_changes: List[SimulationFactorChange]
    projected_recommendations: List[dict] = []
    disclaimer: str = "Scenario projection only. Represents model estimation under simulated operational modifications, not a guaranteed outcome."
