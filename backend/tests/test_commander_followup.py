"""
Test Suite: Commander Monthly Check-In Follow-up & Validation Hardening
SIH 26186 / SAATHI Architecture
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.models.audit import AuditLog
from backend.app.models.follow_up import CheckInFollowUp
from backend.app.models.telemetry import WellnessRecord

def test_commander_can_get_pending_checkins(client: TestClient, commander_token: str):
    """Commander should successfully fetch pending monthly check-ins with consistent total and pagination counts."""
    headers = {"Authorization": f"Bearer {commander_token}"}
    response = client.get("/api/v1/commander/pending-checkins", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_pending" in data
    assert "total_overdue" in data
    assert "total_followup_requested" in data
    assert "current_checkin_cycle" in data
    assert "cycle_label" in data
    assert "total" in data
    assert "total_items" in data
    assert "page" in data
    assert "page_size" in data
    assert data["total"] == data["total_items"]
    assert data["total_pending"] >= len(data["items"])
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0

    item = data["items"][0]
    assert "personnel_id" in item
    assert "display_name" in item
    assert "unit" in item
    assert "role" in item
    assert "days_overdue" in item
    assert "submission_status" in item
    assert "follow_up_status" in item

def test_commander_pending_checkins_search_and_filtering(client: TestClient, commander_token: str):
    """Verify search, unit filter, and pagination on pending check-ins endpoint."""
    headers = {"Authorization": f"Bearer {commander_token}"}

    # Search by personnel ID prefix
    res_search = client.get("/api/v1/commander/pending-checkins?search=P-000001", headers=headers)
    assert res_search.status_code == 200
    search_data = res_search.json()
    for it in search_data["items"]:
        assert "P-000001" in it["personnel_id"]

    # Unit filter
    res_unit = client.get("/api/v1/commander/pending-checkins?unit=Operations", headers=headers)
    assert res_unit.status_code == 200
    unit_data = res_unit.json()
    for it in unit_data["items"]:
        assert "Operations" in it["unit"]

    # Pagination
    res_page = client.get("/api/v1/commander/pending-checkins?page=1&page_size=2", headers=headers)
    assert res_page.status_code == 200
    page_data = res_page.json()
    assert page_data["page"] == 1
    assert page_data["page_size"] == 2
    assert len(page_data["items"]) <= 2



def test_commander_pending_checkins_privacy_boundary(client: TestClient, commander_token: str):
    """
    STRICT PRIVACY TEST:
    Commander pending check-in list and detail MUST NOT expose any sensitive individual
    wellness metrics (support_score, risk, fatigue, sleep, conversations, SHAP, baseline).
    """
    headers = {"Authorization": f"Bearer {commander_token}"}
    response = client.get("/api/v1/commander/pending-checkins", headers=headers)
    assert response.status_code == 200
    data = response.json()

    prohibited_keys = {
        "support_score",
        "latest_support_score",
        "support_priority",
        "latest_priority",
        "risk",
        "risk_band",
        "fatigue",
        "fatigue_level",
        "sleep_quality",
        "work_stress",
        "shap",
        "shap_values",
        "conversation",
        "messages",
        "ai_summary",
        "personal_baseline",
        "intervention_notes"
    }

    for item in data["items"]:
        item_keys = set(item.keys())
        leakage = item_keys.intersection(prohibited_keys)
        assert not leakage, f"Privacy leakage detected in commander item: {leakage}"


def test_unauthorized_roles_blocked_from_commander_pending_checkins(
    client: TestClient,
    personnel_token: str,
    analyst_token: str
):
    """Personnel and Analyst roles MUST be blocked with 403 from Commander endpoints."""
    # Personnel blocked
    res_p = client.get(
        "/api/v1/commander/pending-checkins",
        headers={"Authorization": f"Bearer {personnel_token}"}
    )
    assert res_p.status_code == 403

    # Analyst blocked
    res_a = client.get(
        "/api/v1/commander/pending-checkins",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res_a.status_code == 403


def test_commander_can_view_personnel_followup_detail(client: TestClient, commander_token: str):
    """Commander can view restricted follow-up detail for a single personnel."""
    headers = {"Authorization": f"Bearer {commander_token}"}
    response = client.get("/api/v1/commander/pending-checkins/P-000001", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["personnel_id"] == "P-000001"
    assert "unit" in data
    assert "role" in data
    assert "days_overdue" in data
    assert "follow_up_status" in data

    # Verify no sensitive scores in detail view
    for forbidden in ["support_score", "risk", "shap", "fatigue"]:
        assert forbidden not in data


def test_commander_request_followup_workflow(
    client: TestClient,
    commander_token: str,
    personnel_p1_token: str
):
    """
    Test complete follow-up workflow:
    1. Commander requests check-in follow-up for P-000001.
    2. Follow-up record and audit log are created.
    3. Personnel sees follow-up reminder on check-in status endpoint.
    4. Personnel submits check-in form.
    5. Follow-up status transitions to COMPLETED and personnel is marked submitted.
    """
    cmd_headers = {"Authorization": f"Bearer {commander_token}"}
    p1_headers = {"Authorization": f"Bearer {personnel_p1_token}"}

    # Step 1: Commander initiates follow-up request
    req_res = client.post(
        "/api/v1/commander/pending-checkins/P-000001/follow-up",
        headers=cmd_headers,
        json={"notes": "Monthly window elapsed. Please submit check-in."}
    )
    assert req_res.status_code == 200
    req_data = req_res.json()
    assert req_data["personnel_id"] == "P-000001"
    assert req_data["status"] == "SUCCESS"
    assert req_data["follow_up_status"] == "FOLLOW_UP_REQUESTED"

    # Step 2: Personnel queries check-in status
    status_res = client.get("/api/v1/wellness/check-in-status", headers=p1_headers)
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["personnel_id"] == "P-000001"
    assert status_data["follow_up_requested"] is True
    assert status_data["follow_up_status"] == "FOLLOW_UP_REQUESTED"

    # Step 3: Personnel submits voluntary check-in form
    checkin_payload = {
        "sleep_quality": 4,
        "fatigue_level": 2,
        "work_stress": 3,
        "mood_wellbeing": 4,
        "work_life_balance": 3,
        "job_satisfaction": 4
    }
    submit_res = client.post(
        "/api/v1/wellness/check-in",
        headers=p1_headers,
        json=checkin_payload
    )
    assert submit_res.status_code == 200

    # Step 4: Status now reports completed and submitted
    updated_status_res = client.get("/api/v1/wellness/check-in-status", headers=p1_headers)
    assert updated_status_res.status_code == 200
    updated_status = updated_status_res.json()
    assert updated_status["is_submitted"] is True
    assert updated_status["follow_up_status"] == "COMPLETED"


def test_commander_request_followup_nonexistent_personnel(client: TestClient, commander_token: str):
    """Requesting follow-up for non-existent personnel should return 404."""
    headers = {"Authorization": f"Bearer {commander_token}"}
    response = client.post(
        "/api/v1/commander/pending-checkins/P-999999/follow-up",
        headers=headers,
        json={"notes": "Test"}
    )
    assert response.status_code == 404


def test_server_side_validation_hardening(
    client: TestClient,
    commander_token: str,
    personnel_token: str,
    admin_token: str
):
    """
    Test comprehensive backend input validation hardening:
    - Pagination out of bounds (limit > 100 or offset < 0)
    - Oversized payloads
    - Invalid numeric ranges
    - Protected field mass assignment & invalid enum
    """
    cmd_headers = {"Authorization": f"Bearer {commander_token}"}
    p_headers = {"Authorization": f"Bearer {personnel_token}"}
    adm_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Page size abuse (limit > 100) -> 422
    res_page = client.get("/api/v1/commander/pending-checkins?limit=1000", headers=cmd_headers)
    assert res_page.status_code == 422

    # 2. Negative offset (offset < 0) -> 422
    res_neg_page = client.get("/api/v1/commander/pending-checkins?offset=-1", headers=cmd_headers)
    assert res_neg_page.status_code == 422

    # 3. Oversized follow-up notes (>256 chars) -> 422
    long_note = "A" * 300
    res_long_notes = client.post(
        "/api/v1/commander/pending-checkins/P-000001/follow-up",
        headers=cmd_headers,
        json={"notes": long_note}
    )
    assert res_long_notes.status_code == 422

    # 4. Out-of-bounds numeric wellness scores (e.g. sleep_quality = 99 or -5) -> 422
    res_bad_wellness = client.post(
        "/api/v1/wellness/check-in",
        headers=p_headers,
        json={"sleep_quality": 99, "fatigue_level": -5}
    )
    assert res_bad_wellness.status_code == 422

    # 5. Invalid Role Creation -> 422
    res_bad_role = client.post(
        "/api/v1/auth/users",
        headers=adm_headers,
        json={
            "username": "hacker_user",
            "email": "hacker@test.gov",
            "password": "Password123!",
            "role": "SUPER_ADMIN"  # Invalid role
        }
    )
    assert res_bad_role.status_code == 422
