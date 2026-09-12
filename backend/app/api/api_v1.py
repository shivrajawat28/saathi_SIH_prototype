"""
SAATHI API v1 Main Router Aggregator
"""

from fastapi import APIRouter

from backend.app.api.auth import router as auth_router
from backend.app.api.personnel import router as personnel_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.wellness import router as wellness_router
from backend.app.api.interventions import router as interventions_router
from backend.app.api.simulations import router as simulations_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.audit import router as audit_router
from backend.app.api.commander import router as commander_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(personnel_router)
api_router.include_router(predictions_router)
api_router.include_router(wellness_router)
api_router.include_router(interventions_router)
api_router.include_router(simulations_router)
api_router.include_router(analytics_router)
api_router.include_router(commander_router)
api_router.include_router(audit_router)
