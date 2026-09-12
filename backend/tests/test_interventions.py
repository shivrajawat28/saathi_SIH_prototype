"""
SAATHI Closed-Loop Welfare Intervention & Outcome Tracking Tests
"""

import pytest
from fastapi.testclient import TestClient

def test_create_intervention_authorized(client: TestClient, welfare_token: str):
    payload = {
        "personnel_id": "P-000001",
        "intervention_type": "WORKLOAD_REVIEW",
        "action_summary": "Discussed reducing consecutive night shifts and authorized rest rotation."
    }
    resp = client.post(
        "/api/v1/interventions/",
        json=payload,
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["personnel_id"] == "P-000001"
    assert data["intervention_type"] == "WORKLOAD_REVIEW"
    assert data["status"] == "OPEN"
    assert "intervention_id" in data

def test_create_intervention_unauthorized(client: TestClient, commander_token: str):
    payload = {
        "personnel_id": "P-000001",
        "intervention_type": "WORKLOAD_REVIEW",
        "action_summary": "Unauthorized attempt."
    }
    resp = client.post(
        "/api/v1/interventions/",
        json=payload,
        headers={"Authorization": f"Bearer {commander_token}"}
    )
    assert resp.status_code == 403

def test_record_intervention_outcome(client: TestClient, welfare_token: str):
    # 1. Create intervention
    create_resp = client.post(
        "/api/v1/interventions/",
        json={
            "personnel_id": "P-000002",
            "intervention_type": "RECOVERY_LEAVE",
            "action_summary": "Authorized 4 days restorative leave."
        },
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert create_resp.status_code == 200
    int_id = create_resp.json()["intervention_id"]

    # 2. Record outcome
    outcome_resp = client.post(
        f"/api/v1/interventions/{int_id}/outcomes",
        json={
            "outcome_status": "IMPROVED",
            "follow_up_notes": "Personnel resumed operational duty with normalized workload parameters."
        },
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert outcome_resp.status_code == 200
    data = outcome_resp.json()
    assert data["outcome_status"] == "IMPROVED"
    assert data["intervention_id"] == int_id
