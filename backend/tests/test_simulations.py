"""
SAATHI What-If Counterfactual Simulation Tests
"""

import pytest
from fastapi.testclient import TestClient

def test_counterfactual_simulation_success(client: TestClient, welfare_token: str):
    payload = {
        "reduce_night_shifts": 3,
        "reduce_duty_hours": 20.0,
        "grant_recovery_days": 2
    }
    resp = client.post(
        "/api/v1/simulations/personnel/P-000001",
        json=payload,
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["personnel_id"] == "P-000001"
    assert data["simulation_only"] is True
    assert "current_score" in data
    assert "projected_score" in data
    assert "parameter_changes" in data
    assert len(data["parameter_changes"]) > 0
    assert "disclaimer" in data
    assert "Scenario projection only" in data["disclaimer"]

def test_simulation_unauthorized_personnel(client: TestClient, personnel_p1_token: str):
    payload = {"reduce_night_shifts": 2}
    resp = client.post(
        "/api/v1/simulations/personnel/P-000001",
        json=payload,
        headers={"Authorization": f"Bearer {personnel_p1_token}"}
    )
    assert resp.status_code == 403
