"""
SAATHI: Data Quality and Integrity Validation Test Suite
Tests schema validity, range boundaries, lack of orphan records, and ethical constraints.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from ml.config import (
    OFFICIAL_HR_DIR,
    PROCESSED_DIR,
    SYNTHETIC_DIR,
    DEPLOYMENT_TYPES,
    LOCATION_CATEGORIES,
    LEAVE_TYPES
)

@pytest.fixture(scope="module")
def personnel_master():
    path = PROCESSED_DIR / "personnel_master.csv"
    assert path.exists(), "personnel_master.csv does not exist."
    return pd.read_csv(path)

@pytest.fixture(scope="module")
def deployment_data():
    path = SYNTHETIC_DIR / "deployment" / "deployment_records.csv"
    assert path.exists(), "deployment_records.csv does not exist."
    return pd.read_csv(path)

@pytest.fixture(scope="module")
def leave_data():
    path = SYNTHETIC_DIR / "leave" / "leave_history.csv"
    assert path.exists(), "leave_history.csv does not exist."
    return pd.read_csv(path)

@pytest.fixture(scope="module")
def workload_data():
    path = SYNTHETIC_DIR / "workload" / "workload_records.csv"
    assert path.exists(), "workload_records.csv does not exist."
    return pd.read_csv(path)

@pytest.fixture(scope="module")
def wellness_data():
    path = SYNTHETIC_DIR / "wellness" / "wellness_surveys.csv"
    assert path.exists(), "wellness_surveys.csv does not exist."
    return pd.read_csv(path)

@pytest.fixture(scope="module")
def behavioral_data():
    path = SYNTHETIC_DIR / "behavioral" / "behavioral_records.csv"
    assert path.exists(), "behavioral_records.csv does not exist."
    return pd.read_csv(path)


def test_personnel_master_integrity(personnel_master):
    # Check deduplication and uniqueness
    assert personnel_master['personnel_id'].nunique() == len(personnel_master)
    assert len(personnel_master) == 1470
    assert personnel_master['personnel_id'].str.startswith("P-").all()
    assert not personnel_master['personnel_id'].isnull().any()


def test_no_orphan_records(personnel_master, deployment_data, leave_data, workload_data, wellness_data, behavioral_data):
    valid_ids = set(personnel_master['personnel_id'])
    
    assert set(deployment_data['personnel_id']).issubset(valid_ids)
    assert set(leave_data['personnel_id']).issubset(valid_ids)
    assert set(workload_data['personnel_id']) == valid_ids
    assert set(wellness_data['personnel_id']) == valid_ids
    assert set(behavioral_data['personnel_id']) == valid_ids


def test_workload_boundaries(workload_data):
    # Total monthly rows must be 1470 * 12 = 17640
    assert len(workload_data) == 1470 * 12

    # Verify physical bounds
    assert (workload_data['duty_hours'] >= 80).all() and (workload_data['duty_hours'] <= 350).all()
    assert (workload_data['overtime_hours'] >= 0).all() and (workload_data['overtime_hours'] <= 100).all()
    assert (workload_data['night_shifts'] >= 0).all() and (workload_data['night_shifts'] <= 25).all()
    assert (workload_data['consecutive_duty_days'] >= 1).all() and (workload_data['consecutive_duty_days'] <= 30).all()
    assert (workload_data['rest_hours'] >= 15).all() and (workload_data['rest_hours'] <= 180).all()
    assert (workload_data['workload_score'] >= 0.0).all() and (workload_data['workload_score'] <= 100.0).all()
    assert (workload_data['operational_intensity'] >= 1).all() and (workload_data['operational_intensity'] <= 5).all()


def test_wellness_boundaries(wellness_data):
    assert len(wellness_data) == 1470 * 12

    wellness_cols = [
        'sleep_quality', 'fatigue_level', 'work_stress', 'mood_wellbeing',
        'work_life_balance', 'job_satisfaction', 'recovery_quality', 'self_reported_strain'
    ]
    for col in wellness_cols:
        non_null_vals = wellness_data[col].dropna()
        assert (non_null_vals >= 1.0).all(), f"Values in {col} below 1.0"
        assert (non_null_vals <= 5.0).all(), f"Values in {col} above 5.0"


def test_deployment_and_leave_categoricals(deployment_data, leave_data):
    assert set(deployment_data['deployment_type']).issubset(set(DEPLOYMENT_TYPES))
    assert set(deployment_data['location_category']).issubset(set(LOCATION_CATEGORIES))
    assert (deployment_data['deployment_duration_days'] > 0).all()
    assert (deployment_data['operational_intensity'] >= 1).all() and (deployment_data['operational_intensity'] <= 5).all()

    assert set(leave_data['leave_type']).issubset(set(LEAVE_TYPES))
    assert (leave_data['duration_days'] > 0).all()
    assert (leave_data['days_since_previous_leave'] >= 0).all()


def test_no_surveillance_fields(behavioral_data, workload_data, wellness_data):
    forbidden_terms = ['facial', 'voice', 'gps', 'location_tracking', 'message', 'social_media', 'camera', 'depression', 'mental_illness']
    for df in [behavioral_data, workload_data, wellness_data]:
        for col in df.columns:
            for term in forbidden_terms:
                assert term not in col.lower(), f"Forbidden surveillance or clinical term '{term}' found in column '{col}'"
