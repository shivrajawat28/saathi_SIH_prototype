"""
SAATHI Aggregated Analytics Pydantic Schemas (Commander & Analyst View)
"""

from typing import List, Dict
from pydantic import BaseModel

class PriorityCount(BaseModel):
    priority: str # GREEN, YELLOW, ORANGE, RED
    count: int
    percentage: float

class DepartmentWelfareSummary(BaseModel):
    department: str
    total_personnel: int
    green_count: int
    yellow_count: int
    orange_count: int
    red_count: int
    avg_support_score: float

class CommanderAnalyticsResponse(BaseModel):
    total_strength: int
    high_risk_total: int
    priority_distribution: List[PriorityCount]
    department_breakdown: List[DepartmentWelfareSummary]
    interventions_active_count: int
    interventions_improved_count: int
    data_completeness_avg: float
    disclaimer: str = "Aggregated operational readiness and welfare support statistics. Contains zero private medical or sensitive survey text."
