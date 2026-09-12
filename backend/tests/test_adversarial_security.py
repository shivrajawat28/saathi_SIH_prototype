"""
SAATHI Adversarial Security & IDOR Penetration Tests
Verifies that unauthorized roles and cross-personnel ID tampering are strictly rejected.
"""

import pytest
from fastapi.testclient import TestClient

def test_analyst_blocked_from_individual_lookup(client: TestClient, analyst_token: str):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    response = client.get("/api/v1/personnel/P-000001", headers=headers)
    assert response.status_code == 403
    assert "Analysts are restricted" in response.json()["detail"]

def test_commander_blocked_from_individual_timeline(client: TestClient, commander_token: str):
    headers = {"Authorization": f"Bearer {commander_token}"}
    response = client.get("/api/v1/personnel/P-000001/timeline", headers=headers)
    assert response.status_code == 403
    assert "restricted" in response.json()["detail"].lower()

def test_commander_blocked_from_individual_prediction(client: TestClient, commander_token: str):
    headers = {"Authorization": f"Bearer {commander_token}"}
    response = client.post("/api/v1/predictions/personnel/P-000001", headers=headers)
    assert response.status_code == 403

def test_analyst_blocked_from_batch_triage(client: TestClient, analyst_token: str):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    response = client.get("/api/v1/predictions/batch-triage", headers=headers)
    assert response.status_code == 403

def test_commander_blocked_from_simulation(client: TestClient, commander_token: str):
    headers = {"Authorization": f"Bearer {commander_token}"}
    payload = {"reduce_duty_hours": 20.0, "reduce_night_shifts": 4}
    response = client.post("/api/v1/simulations/personnel/P-000001", json=payload, headers=headers)
    assert response.status_code == 403

def test_personnel_blocked_from_other_personnel_prediction(client: TestClient, personnel_p1_token: str):
    # officer_p1 is P-000001, attempts to run prediction on P-000002
    headers = {"Authorization": f"Bearer {personnel_p1_token}"}
    response = client.post("/api/v1/predictions/personnel/P-000002", headers=headers)
    assert response.status_code == 403

def test_personnel_blocked_from_other_personnel_interventions(client: TestClient, personnel_p1_token: str):
    headers = {"Authorization": f"Bearer {personnel_p1_token}"}
    response = client.get("/api/v1/interventions/personnel/P-000002", headers=headers)
    assert response.status_code == 403

def test_simulation_validation_rejects_negative_inputs(client: TestClient, welfare_token: str):
    headers = {"Authorization": f"Bearer {welfare_token}"}
    payload = {"reduce_duty_hours": -20.0, "reduce_night_shifts": -5}
    response = client.post("/api/v1/simulations/personnel/P-000001", json=payload, headers=headers)
    assert response.status_code == 422  # Validation error on negative constraints

def test_rate_limiter_blocks_excessive_rapid_requests(client: TestClient):
    from backend.app.core.rate_limit import rate_limiter
    # Test rate limiter directly
    key = "test_client_ip:/api/v1/auth/login"
    # First 15 allowed
    for _ in range(15):
        allowed, remaining, _ = rate_limiter.check_rate_limit(key, max_requests=15, window_seconds=60)
        assert allowed is True
    # 16th rejected
    allowed, remaining, retry_after = rate_limiter.check_rate_limit(key, max_requests=15, window_seconds=60)
    assert allowed is False
    assert retry_after > 0
