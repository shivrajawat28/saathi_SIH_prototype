"""
SAATHI Analytics, Voluntary Telemetry & Baseline Leakage Tests
"""

import pytest
from fastapi.testclient import TestClient
import pandas as pd
from backend.app.ml.adapter import ml_adapter

def test_commander_analytics_endpoint(client: TestClient, commander_token: str):
    resp = client.get(
        "/api/v1/analytics/commander-overview",
        headers={"Authorization": f"Bearer {commander_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_strength" in data
    assert "priority_distribution" in data
    assert "department_breakdown" in data
    assert "disclaimer" in data
    assert "zero private medical" in data["disclaimer"].lower()

def test_voluntary_wellness_check_in(client: TestClient, personnel_p1_token: str):
    payload = {
        "sleep_quality": 4.0,
        "fatigue_level": 2.0,
        "work_stress": 2.5,
        "mood_wellbeing": 4.0
    }
    resp = client.post(
        "/api/v1/wellness/check-in",
        json=payload,
        headers={"Authorization": f"Bearer {personnel_p1_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"

def test_data_completeness_gate_insufficient_data():
    # Construct an observation with only 1 signal present (completeness = 1/8 = 0.125 < 0.35)
    row_dict = {
        "personnel_id": "P-COLDSTART",
        "duty_hours": 160.0,
        "overtime_hours": None,
        "night_shifts": None,
        "rest_hours": None,
        "sleep_quality": None,
        "fatigue_level": None,
        "self_reported_strain": None,
        "routine_deviation": None,
        "baseline_available": False,
        "history_periods_count": 0
    }
    obs_df = pd.DataFrame([row_dict])
    res = ml_adapter.predict_observation(obs_df)
    assert res["status"] == "INSUFFICIENT_DATA"
    assert res["priority"] == "INSUFFICIENT_DATA"
    assert res["support_score"] is None
    assert res["data_completeness"] < 0.35

def test_causal_baseline_leakage_prevention():
    # Verify that personal baseline statistics strictly use t <= T - 1 observations
    from ml.baseline.personal_baseline import PersonalBaselineEngine
    engine = PersonalBaselineEngine(min_history_periods=3, window_size=4)
    df = pd.DataFrame([
        {"personnel_id": "P-TEST", "month_idx": 1, "duty_hours": 160.0, "night_shifts": 2},
        {"personnel_id": "P-TEST", "month_idx": 2, "duty_hours": 170.0, "night_shifts": 3},
        {"personnel_id": "P-TEST", "month_idx": 3, "duty_hours": 165.0, "night_shifts": 2},
        {"personnel_id": "P-TEST", "month_idx": 4, "duty_hours": 220.0, "night_shifts": 8}, # target month T
    ])
    
    res_df = engine.compute_personnel_baselines(df, ["duty_hours", "night_shifts"])
    m4_row = res_df[res_df["month_idx"] == 4].iloc[0]
    
    # Baseline for month 4 should ONLY be computed from months 1-3
    expected_mean = (160.0 + 170.0 + 165.0) / 3.0
    assert m4_row["duty_hours_personal_mean"] == expected_mean
    # The 220.0 duty hours at T must NOT be in the mean
    assert m4_row["duty_hours_personal_mean"] < 170.0
