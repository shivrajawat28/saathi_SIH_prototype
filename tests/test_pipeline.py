"""
SAATHI: End-to-End Pipeline & Prediction Service Unit Tests
"""

import pytest
import pandas as pd
import numpy as np
from ml.predict import WelfarePredictionService
from ml.config import SUPPORT_PRIORITIES, PROCESSED_DIR

@pytest.fixture(scope="module")
def prediction_service():
    return WelfarePredictionService()

@pytest.fixture(scope="module")
def sample_test_record():
    data_path = PROCESSED_DIR / "integrated_longitudinal.parquet"
    if not data_path.exists():
        data_path = PROCESSED_DIR / "integrated_longitudinal.csv"
        df = pd.read_csv(data_path)
    else:
        df = pd.read_parquet(data_path)
    return df[df['month_idx'] == 11].iloc[[0]]

def test_valid_prediction_structure(prediction_service, sample_test_record):
    res = prediction_service.predict_personnel(sample_test_record)

    assert res["status"] == "VALID"
    assert res["support_priority"] in SUPPORT_PRIORITIES
    assert 0.0 <= res["score"] <= 100.0
    assert 0.0 <= res["confidence"] <= 1.0
    assert 0.0 <= res["data_completeness"] <= 1.0
    assert isinstance(res["baseline_available"], bool)
    assert isinstance(res["top_factors"], list)
    assert len(res["top_factors"]) > 0

    # Verify factor structure
    for f in res["top_factors"]:
        assert "factor" in f
        assert "direction" in f
        assert f["direction"] in ["increase", "decrease"]
        assert "contribution" in f
        assert isinstance(f["contribution"], float)

def test_insufficient_data_rejection(prediction_service, sample_test_record):
    incomplete_record = sample_test_record.copy()
    # Nullify all key signals
    for col in ['duty_hours', 'overtime_hours', 'night_shifts', 'rest_hours', 'sleep_quality', 'fatigue_level', 'self_reported_strain']:
        incomplete_record[col] = np.nan

    res = prediction_service.predict_personnel(incomplete_record)
    assert res["status"] == "INSUFFICIENT_DATA"
    assert res["support_priority"] == "INSUFFICIENT_DATA"
    assert res["score"] is None
    assert res["confidence"] == 0.0
    assert res["data_completeness"] < 0.35

def test_no_forbidden_terms_in_output(prediction_service, sample_test_record):
    forbidden = ["depressed", "mental illness", "psychologically unfit", "dangerous", "disorder", "punishment", "disciplinary"]
    res = prediction_service.predict_personnel(sample_test_record)
    
    # Check priority label and factor descriptions
    priority_text = str(res["support_priority"]).lower()
    description_text = str(res["description"]).lower()
    factors_text = " ".join([f["factor"].lower() for f in res["top_factors"]])

    for term in forbidden:
        assert term not in priority_text, f"Forbidden term '{term}' in priority label!"
        assert term not in description_text, f"Forbidden term '{term}' in description!"
        assert term not in factors_text, f"Forbidden term '{term}' in factors!"
