"""
SAATHI Prediction Pipeline & Decision Support API Tests
"""

import pytest
from fastapi.testclient import TestClient

def test_valid_prediction_generation(client: TestClient, welfare_token: str):
    resp = client.post(
        "/api/v1/predictions/personnel/P-000001",
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["personnel_id"] == "P-000001"
    assert "support_score" in data
    assert 0.0 <= data["support_score"] <= 100.0
    assert data["priority"] in ["GREEN", "YELLOW", "ORANGE", "RED"]
    assert "prediction_reliability" in data
    assert 0.0 <= data["prediction_reliability"] <= 1.0
    assert "data_completeness" in data
    assert len(data["top_factors"]) > 0
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert "human_review_required" in data

def test_priority_tier_mapping_consistency(client: TestClient, welfare_token: str):
    resp = client.post(
        "/api/v1/predictions/personnel/P-000001",
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    score = data["support_score"]
    priority = data["priority"]
    if score < 30.0:
        assert priority == "GREEN"
    elif score < 55.0:
        assert priority == "YELLOW"
    elif score < 75.0:
        assert priority == "ORANGE"
    else:
        assert priority == "RED"

def test_nonexistent_personnel_prediction(client: TestClient, welfare_token: str):
    resp = client.post(
        "/api/v1/predictions/personnel/P-999999",
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert resp.status_code == 400
    assert "not found" in resp.json()["detail"].lower()

def test_batch_triage_dashboard(client: TestClient, welfare_token: str):
    resp = client.get(
        "/api/v1/predictions/batch-triage?limit=10",
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) > 0
    assert "personnel_id" in items[0]
    assert "support_score" in items[0]
    assert "priority" in items[0]
