"""
SAATHI Core Configuration
Uses Pydantic BaseSettings for environment-driven configuration.
"""

import os
import json
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "SAATHI AI Welfare Decision Support System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = "saathi-sih-production-secure-jwt-secret-key-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # Database
    DATABASE_URL: str = "sqlite:///./saathi.db"

    # ML Artifacts (Relative to backend directory or workspace root)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    MODEL_PATH: str = str(BASE_DIR / "ml/models/support_priority_model.joblib")
    METADATA_PATH: str = str(BASE_DIR / "ml/models/model_metadata.json")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000"
    ]

    # Initial Admin
    INITIAL_ADMIN_USERNAME: str = "admin"
    INITIAL_ADMIN_EMAIL: str = "admin@forces.gov.in"
    INITIAL_ADMIN_PASSWORD: str = "AdminSecurePassword123!"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        env = os.getenv("ENVIRONMENT", "development").lower()
        if env == "production":
            if not v or v == "saathi-sih-production-secure-jwt-secret-key-change-in-prod" or len(v) < 32:
                raise ValueError("In production, SECRET_KEY must be an environment-provided strong secret (min 32 chars).")
        return v

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
