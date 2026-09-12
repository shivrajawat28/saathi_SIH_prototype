"""
SAATHI Role-Based Access Control (RBAC) & Privacy Tests
"""

import pytest
from fastapi.testclient import TestClient

def test_admin_can_access_audit_logs(client: TestClient, admin_token: str):
    resp = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_welfare_officer_cannot_access_audit_logs(client: TestClient, welfare_token: str):
    resp = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert resp.status_code == 403
    assert "forbidden" in resp.json()["detail"].lower()

def test_personnel_cannot_access_other_personnel_profile(client: TestClient, personnel_p1_token: str):
    # P1 tries to access P2's profile
    resp = client.get(
        "/api/v1/personnel/P-000002",
        headers={"Authorization": f"Bearer {personnel_p1_token}"}
    )
    assert resp.status_code == 403
    assert "only permitted to view their own profile" in resp.json()["detail"]

def test_personnel_can_access_own_profile(client: TestClient, personnel_p1_token: str):
    resp = client.get(
        "/api/v1/personnel/P-000001",
        headers={"Authorization": f"Bearer {personnel_p1_token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["job_role"] == "Field Specialist"

def test_commander_restricted_from_subjective_survey_text(client: TestClient, commander_token: str):
    # Commander views personnel timeline
    resp = client.get(
        "/api/v1/personnel/P-000001/timeline",
        headers={"Authorization": f"Bearer {commander_token}"}
    )
    if resp.status_code == 200:
        timeline = resp.json()["timeline"]
        for item in timeline:
            assert item["self_reported_strain"] is None
            assert item["sleep_quality"] is None
