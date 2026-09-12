"""
SAATHI Backend Application Entrypoint
FastAPI-based Predictive Personnel Stress and Welfare Monitoring Decision Support API
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.api.api_v1 import api_router
from backend.app.db.init_db import init_db
from backend.app.ml.adapter import MLAdapter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and seed if empty
    print("Starting SAATHI Backend Service...")
    init_db()
    # Preload Locked ML Model Pipeline
    print("Preloading Locked ML Model Pipeline...")
    _ = MLAdapter.get_instance()
    print("SAATHI Backend Service initialized successfully.")
    yield
    print("Shutting down SAATHI Backend Service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    description=(
        "SAATHI: AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces. "
        "A non-diagnostic, decision-support backend providing calibrated welfare support priorities, "
        "personal historical baseline change detection, explainable factor attribution, and closed-loop intervention tracking."
    ),
    lifespan=lifespan
)

# CORS Configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health", tags=["System"])
def health_check():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "SAATHI Welfare Decision Support API",
        "version": "1.0.0",
        "ml_engine": "Balanced Random Forest + Platt Calibration (Locked)",
        "decision_support_only": True
    }

@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to SAATHI Welfare Support Decision System API",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

# Include v1 API Router
app.include_router(api_router, prefix=settings.API_V1_STR)
