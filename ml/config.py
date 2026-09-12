"""
SAATHI: AI-Based Predictive Personnel Stress and Welfare Monitoring System
Global Configuration & Schema Definitions
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OFFICIAL_HR_DIR = DATA_DIR / "official_hr"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PROCESSED_DIR = DATA_DIR / "processed"
PROFILING_DIR = DATA_DIR / "profiling"

ML_DIR = BASE_DIR / "ml"
MODELS_DIR = ML_DIR / "models"
RESULTS_DIR = ML_DIR / "results"

# Ensure all output directories exist
for directory in [
    DATA_DIR,
    OFFICIAL_HR_DIR,
    SYNTHETIC_DIR / "deployment",
    SYNTHETIC_DIR / "leave",
    SYNTHETIC_DIR / "workload",
    SYNTHETIC_DIR / "wellness",
    SYNTHETIC_DIR / "behavioral",
    PROCESSED_DIR,
    PROFILING_DIR,
    MODELS_DIR,
    RESULTS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Random Seed for complete reproducibility
RANDOM_SEED = 42

# Simulation Parameters
LONGITUDINAL_MONTHS = 12
START_DATE = "2025-01-01"

# Welfare Priority Categories (Decision Support Only - No Medical Diagnosis)
SUPPORT_PRIORITIES = ["GREEN", "YELLOW", "ORANGE", "RED"]
PRIORITY_DESCRIPTIONS = {
    "GREEN": "Stable - Normal occupational and recovery pattern",
    "YELLOW": "Early Strain Indicators - Minor workload surge or reduced recovery",
    "ORANGE": "Persistent Elevated Strain - Sustained operational stress requiring check-in",
    "RED": "Priority Welfare Review - Multi-signal cumulative strain warranting proactive outreach",
}

PRIORITY_TO_NUM = {"GREEN": 0, "YELLOW": 1, "ORANGE": 2, "RED": 3}
NUM_TO_PRIORITY = {0: "GREEN", 1: "YELLOW", 2: "ORANGE", 3: "RED"}

# Score Thresholds for Support Priority
SCORE_THRESHOLDS = {
    "GREEN": (0.0, 30.0),
    "YELLOW": (30.0, 55.0),
    "ORANGE": (55.0, 75.0),
    "RED": (75.0, 100.0),
}

# Deployment categorical choices
DEPLOYMENT_TYPES = ["Routine", "Extended", "High Tempo", "Training/Operational"]
LOCATION_CATEGORIES = ["Urban Base", "Semi-Urban Outpost", "Remote/Difficult Terrain", "High Altitude/Extreme"]

# Leave categorical choices
LEAVE_TYPES = ["Annual", "Casual", "Medical/Authorized", "Recovery", "Other Authorized"]

# Time-Aware Splits (in months 1 to 12)
TRAIN_MONTHS = list(range(1, 9))      # Months 1-8
VAL_MONTHS = list(range(9, 11))       # Months 9-10
TEST_MONTHS = list(range(11, 13))     # Months 11-12
