"""
SAATHI Prediction & Decision Support Pydantic Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class TopFactorSchema(BaseModel):
    factor: str
    direction: str # increase, decrease
    contribution: float = Field(..., description="Estimated percentage attribution")

class RecommendationSchema(BaseModel):
    type: str # WORKLOAD_REVIEW, RECOVERY_LEAVE, WELFARE_CHECK_IN, etc.
    priority: str # LOW, MEDIUM, HIGH
    reason: str

class PredictionResponse(BaseModel):
    personnel_id: str
    status: str = "VALID" # VALID, INSUFFICIENT_DATA, ERROR
    support_score: Optional[float] = None
    priority: str # GREEN, YELLOW, ORANGE, RED, INSUFFICIENT_DATA
    high_risk_probability: Optional[float] = None
    prediction_reliability: float
    data_completeness: float
    baseline_maturity_months: int
    operating_threshold: float = 0.50
    top_factors: List[TopFactorSchema] = []
    recommendations: List[RecommendationSchema] = []
    human_review_required: bool = False
    message: Optional[str] = None
    ethical_guardrail: str = "Authorized decision support only. Identifies occupational welfare review priority; not a clinical assessment or punitive tool."

class BatchTriageItem(BaseModel):
    personnel_id: str
    department: Optional[str] = "Operations"
    job_role: Optional[str] = "Field Specialist"
    support_score: float
    priority: str
    high_risk_probability: Optional[float] = None
    prediction_reliability: float = 0.85
    data_completeness: float = 1.0
    human_review_required: bool = False
    predicted_at: Optional[datetime] = None

class BatchTriageResponse(BaseModel):
    total_analyzed: int
    high_risk_count: int
    priority_distribution: dict
    items: List[BatchTriageItem]
