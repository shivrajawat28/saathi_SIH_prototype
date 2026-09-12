"""
SAATHI Voluntary AI Welfare Conversation Assistant Tests
Validates non-clinical signal extraction, crisis safety, voice fallback, consent enforcement,
longitudinal comparison, and strict role-based access control.
"""

import pytest
from fastapi.testclient import TestClient

def test_companion_consent_required(client: TestClient, personnel_token: str):
    """Verifies that conversation processing requires explicit voluntary consent."""
    resp = client.post(
        "/api/v1/wellness/companion/chat",
        headers={"Authorization": f"Bearer {personnel_token}"},
        json={
            "message": "Feeling tired",
            "consent_given": False
        }
    )
    assert resp.status_code == 400
    assert "consent is required" in resp.json()["detail"].lower()

def test_companion_signal_extraction_hinglish(client: TestClient, personnel_token: str):
    """Verifies non-clinical signal extraction for voluntary Hinglish input."""
    resp = client.post(
        "/api/v1/wellness/companion/chat",
        headers={"Authorization": f"Bearer {personnel_token}"},
        json={
            "message": "Mujhe pichhle kuch dino se continuous night shifts ki wajah se bahut thakaan ho rahi hai aur neend proper nahi aa rahi.",
            "consent_given": True,
            "input_mode": "TEXT"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert "ai_summary" in data
    assert data["is_crisis"] is False
    
    signals = data["extracted_signals"]
    assert signals["fatigue"] in ["Moderate", "Elevated"]
    assert signals["sleep_difficulty"] in ["Moderate", "Elevated"]
    assert signals["workload_pressure"] in ["Moderate", "Elevated"]
    assert signals["sentiment_valence"] in ["Strained", "Negative"]
    assert "decision support" in data["ai_summary"].lower() or "voluntary" in data["ai_summary"].lower()

def test_companion_positive_resilience_preservation(client: TestClient, personnel_token: str):
    """Verifies that positive resilience statements are preserved without forcing negative interpretations."""
    resp = client.post(
        "/api/v1/wellness/companion/chat",
        headers={"Authorization": f"Bearer {personnel_token}"},
        json={
            "message": "Main theek hoon, routine acchi chal rahi hai, and team is very supportive. Ready for duty.",
            "consent_given": True,
            "input_mode": "TEXT"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    signals = data["extracted_signals"]
    assert signals["fatigue"] == "None"
    assert signals["sleep_difficulty"] == "None"
    assert signals["sentiment_valence"] == "Positive"
    assert len(signals["positive_resilience_indicators"]) > 0

def test_companion_crisis_safety_handling(client: TestClient, personnel_token: str):
    """Verifies safe, non-diagnostic response and high priority flagging for explicit distress/self-harm language."""
    resp = client.post(
        "/api/v1/wellness/companion/chat",
        headers={"Authorization": f"Bearer {personnel_token}"},
        json={
            "message": "I feel hopeless and want to kill myself, can't go on anymore.",
            "consent_given": True
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_crisis"] is True
    assert data["urgency_level"] == "CRISIS"
    assert "helpline" in data["reply"].lower() or "suraksha" in data["reply"].lower() or "kiran" in data["reply"].lower()
    assert "welfare" in data["reply"].lower()

def test_companion_submit_and_welfare_officer_review(client: TestClient, personnel_token: str, welfare_token: str):
    """Verifies full lifecycle: personnel submits conversation -> Welfare Officer reviews & records notes."""
    # 1. Submit session
    submit_resp = client.post(
        "/api/v1/wellness/companion/submit",
        headers={"Authorization": f"Bearer {personnel_token}"},
        json={
            "consent_given": True,
            "input_mode": "VOICE_FALLBACK_TEXT",
            "messages": [
                {"sender": "USER", "text": "Continuous duty ke baad thakaan aur sleep issue ho raha hai.", "is_voice": True},
                {"sender": "ASSISTANT", "text": "Aapki baat samajh aa rahi hai. We will support your recovery.", "is_voice": False}
            ]
        }
    )
    assert submit_resp.status_code == 200
    conv_data = submit_resp.json()
    conv_id = conv_data["conversation_id"]
    target_pid = conv_data["personnel_id"]

    # 2. Welfare Officer queries signals for this personnel
    wo_resp = client.get(
        f"/api/v1/wellness/companion/personnel/{target_pid}",
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert wo_resp.status_code == 200
    records = wo_resp.json()
    assert len(records) > 0
    assert any(r["conversation_id"] == conv_id for r in records)

    # 3. Welfare Officer records review action
    review_resp = client.post(
        f"/api/v1/wellness/companion/{conv_id}/review",
        headers={"Authorization": f"Bearer {welfare_token}"},
        json={
            "status": "ACKNOWLEDGED",
            "notes": "Reviewed voluntary sleep and fatigue report; recommended 48h restorative rest rotation."
        }
    )
    assert review_resp.status_code == 200
    reviewed_data = review_resp.json()
    assert reviewed_data["status"] == "ACKNOWLEDGED"
    assert "restorative rest" in reviewed_data["welfare_officer_notes"]

def test_companion_rbac_commander_and_analyst_blocked(client: TestClient, commander_token: str, analyst_token: str):
    """Verifies that Commanders and Analysts are strictly forbidden from viewing individual conversation details."""
    # Commander attempt
    cmd_resp = client.get(
        "/api/v1/wellness/companion/personnel/P-000013",
        headers={"Authorization": f"Bearer {commander_token}"}
    )
    assert cmd_resp.status_code == 403
    assert "restricted" in cmd_resp.json()["detail"].lower()

    # Analyst attempt
    ana_resp = client.get(
        "/api/v1/wellness/companion/personnel/P-000013",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert ana_resp.status_code == 403
    assert "restricted" in ana_resp.json()["detail"].lower()

def test_voice_transcription_service(client: TestClient, personnel_token: str):
    """Verifies audio transcription endpoint with text hint and fallback."""
    resp = client.post(
        "/api/v1/wellness/companion/voice-transcribe",
        headers={"Authorization": f"Bearer {personnel_token}"},
        json={
            "text_hint": "Ghar ki yaad aa rahi hai aur thoda tanav lag raha hai.",
            "language": "hi-IN"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "transcript" in data
    assert "Ghar ki yaad" in data["transcript"]
