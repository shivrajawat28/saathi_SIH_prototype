"""
SAATHI Deployment Readiness Verification Script
Validates all demo accounts, P-000013, P-000001, ML inference,
Wellness Companion, Commander, Analyst, Personnel, Admin,
and Follow-up endpoints.
"""

import sys
import json
import requests

BASE_URL = "http://127.0.0.1:8000"

def log_pass(msg):
    print(f"  [✓ PASS] {msg}")

def log_fail(msg):
    print(f"  [✗ FAIL] {msg}")
    sys.exit(1)

def test_health():
    print("\n--- 1. Health Check ---")
    res = requests.get(f"{BASE_URL}/health")
    if res.status_code == 200 and res.json().get("status") == "healthy":
        log_pass("Backend health check is healthy")
    else:
        log_fail(f"Health check failed: {res.status_code} {res.text}")

def test_demo_accounts():
    print("\n--- 2. Demo Accounts Authentication (Standard & Capitalized Passwords) ---")
    credentials_to_test = [
        ("welfare_officer", "Welfare@123", "WELFARE_OFFICER"),
        ("welfare_officer", "welfare123", "WELFARE_OFFICER"),
        ("commander", "Commander@123", "COMMANDER"),
        ("commander", "commander123", "COMMANDER"),
        ("personnel_p13", "Personnel@123", "PERSONNEL"),
        ("personnel_p13", "personnel123", "PERSONNEL"),
        ("officer_p1", "Personnel@123", "PERSONNEL"),
        ("officer_p1", "personnel123", "PERSONNEL"),
        ("analyst", "Analyst@123", "ANALYST"),
        ("analyst", "analyst123", "ANALYST"),
        ("admin", "Admin@123", "ADMIN"),
        ("admin", "admin123", "ADMIN"),
        ("admin", "AdminSecurePassword123!", "ADMIN")
    ]

    tokens = {}
    for uname, pwd, expected_role in credentials_to_test:
        res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"username": uname, "password": pwd})
        if res.status_code == 200:
            data = res.json()
            assert "access_token" in data, f"No access token for {uname}"
            assert data["user"]["role"] == expected_role, f"Role mismatch for {uname}: expected {expected_role}, got {data['user']['role']}"
            tokens[uname] = data["access_token"]
            log_pass(f"Authenticated {uname} successfully with '{pwd}' -> role: {expected_role}")
        else:
            log_fail(f"Failed to authenticate {uname} with '{pwd}': {res.status_code} {res.text}")

    return tokens

def test_personnel_records(welfare_token):
    print("\n--- 3. Verify P-000013 and P-000001 Profiles & Metrics ---")
    headers = {"Authorization": f"Bearer {welfare_token}"}
    
    # Test P-000013 Profile & Timeline
    res13 = requests.get(f"{BASE_URL}/api/v1/personnel/P-000013", headers=headers)
    if res13.status_code == 200:
        p13_hr = res13.json()
        assert "department" in p13_hr
        assert "job_role" in p13_hr
        log_pass(f"P-000013 HR profile retrieved: {p13_hr.get('department')}, {p13_hr.get('job_role')}")
    else:
        log_fail(f"Failed to retrieve P-000013: {res13.status_code} {res13.text}")

    t13 = requests.get(f"{BASE_URL}/api/v1/personnel/P-000013/timeline", headers=headers)
    if t13.status_code == 200:
        p13_timeline = t13.json()
        assert p13_timeline["personnel_id"] == "P-000013"
        assert len(p13_timeline["timeline"]) > 0
        log_pass(f"P-000013 timeline retrieved with {len(p13_timeline['timeline'])} historical periods")
    else:
        log_fail(f"Failed to retrieve P-000013 timeline: {t13.status_code} {t13.text}")

    # Test P-000001 Profile & Timeline
    res1 = requests.get(f"{BASE_URL}/api/v1/personnel/P-000001", headers=headers)
    if res1.status_code == 200:
        p1_hr = res1.json()
        assert "department" in p1_hr
        log_pass(f"P-000001 HR profile retrieved: {p1_hr.get('department')}, {p1_hr.get('job_role')}")
    else:
        log_fail(f"Failed to retrieve P-000001: {res1.status_code} {res1.text}")

    t1 = requests.get(f"{BASE_URL}/api/v1/personnel/P-000001/timeline", headers=headers)
    if t1.status_code == 200:
        p1_timeline = t1.json()
        assert p1_timeline["personnel_id"] == "P-000001"
        assert len(p1_timeline["timeline"]) > 0
        log_pass(f"P-000001 timeline retrieved with {len(p1_timeline['timeline'])} historical periods")
    else:
        log_fail(f"Failed to retrieve P-000001 timeline: {t1.status_code} {t1.text}")

def test_ml_inference(welfare_token):
    print("\n--- 4. ML Inference & Explainability ---")
    headers = {"Authorization": f"Bearer {welfare_token}"}
    res = requests.post(f"{BASE_URL}/api/v1/predictions/personnel/P-000013?operating_threshold=0.5", headers=headers)
    if res.status_code == 200:
        pred = res.json()
        assert pred["personnel_id"] == "P-000013"
        assert "support_score" in pred
        assert "priority" in pred
        assert len(pred.get("top_factors", [])) > 0
        assert len(pred.get("recommendations", [])) > 0
        log_pass(f"ML inference successful for P-000013: Score={pred['support_score']}, Priority={pred['priority']}")
    else:
        log_fail(f"ML inference failed: {res.status_code} {res.text}")

def test_wellness_companion(p13_token, welfare_token):
    print("\n--- 5. Wellness Companion & Non-Clinical Signal Extraction ---")
    p13_headers = {"Authorization": f"Bearer {p13_token}"}
    welfare_headers = {"Authorization": f"Bearer {welfare_token}"}

    # Personnel sends voluntary check-in
    msg = "Mujhe pichhle kuch dino se continuous night shifts ki wajah se bahut thakaan ho rahi hai aur neend proper nahi aa rahi."
    res = requests.post(f"{BASE_URL}/api/v1/wellness/companion/chat", json={"message": msg}, headers=p13_headers)
    if res.status_code == 200:
        chat_data = res.json()
        assert "reply" in chat_data
        assert "extracted_signals" in chat_data
        log_pass(f"Companion conversational reply received: '{chat_data['reply'][:60]}...'")
        log_pass(f"Extracted non-clinical signals: fatigue={chat_data['extracted_signals'].get('fatigue')}, sleep={chat_data['extracted_signals'].get('sleep_difficulty')}")
    else:
        log_fail(f"Companion chat failed: {res.status_code} {res.text}")

    # Welfare officer reads extracted summary
    summary_res = requests.get(f"{BASE_URL}/api/v1/wellness/companion/personnel/P-000013", headers=welfare_headers)
    if summary_res.status_code == 200:
        summary_list = summary_res.json()
        assert isinstance(summary_list, list)
        log_pass(f"Welfare officer retrieved voluntary signal history: {len(summary_list)} session records")
    else:
        log_fail(f"Failed to fetch companion summary: {summary_res.status_code} {summary_res.text}")

def test_commander_portal(commander_token):
    print("\n--- 6. Commander Dashboard & Aggregate Restrictions ---")
    headers = {"Authorization": f"Bearer {commander_token}"}
    res = requests.get(f"{BASE_URL}/api/v1/analytics/commander-overview", headers=headers)
    if res.status_code == 200:
        overview = res.json()
        assert "total_strength" in overview
        assert "priority_distribution" in overview
        log_pass(f"Commander aggregate overview: Total Strength={overview['total_strength']}, High Risk Total={overview.get('high_risk_total', 0)}")
    else:
        log_fail(f"Commander overview failed: {res.status_code} {res.text}")

    # Verify IDOR / Survey restriction for commander
    survey_res = requests.get(f"{BASE_URL}/api/v1/wellness/companion/personnel/P-000013", headers=headers)
    if survey_res.status_code == 403:
        log_pass("Commander correctly FORBIDDEN (403) from viewing private individual companion signals")
    else:
        log_fail(f"Security error: Commander was able to access private companion records! Status: {survey_res.status_code}")

def test_analyst_portal(analyst_token):
    print("\n--- 7. Analyst Dashboard ---")
    headers = {"Authorization": f"Bearer {analyst_token}"}
    res = requests.get(f"{BASE_URL}/api/v1/analytics/commander-overview", headers=headers)
    if res.status_code == 200:
        overview = res.json()
        assert "department_breakdown" in overview
        log_pass(f"Analyst accessed aggregated distribution: {len(overview['department_breakdown'])} departments analyzed")
    else:
        log_fail(f"Analyst overview failed: {res.status_code} {res.text}")

def test_admin_portal(admin_token):
    print("\n--- 8. Admin Audit Portal ---")
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = requests.get(f"{BASE_URL}/api/v1/audit/logs?limit=10", headers=headers)
    if res.status_code == 200:
        logs = res.json()
        assert isinstance(logs, list)
        log_pass(f"Admin audit logs retrieved: {len(logs)} entries")
    else:
        log_fail(f"Admin audit logs failed: {res.status_code} {res.text}")

def test_monthly_checkin_followup(welfare_token, commander_token):
    print("\n--- 9. Monthly Check-In Follow-up Flow ---")
    welfare_headers = {"Authorization": f"Bearer {welfare_token}"}
    commander_headers = {"Authorization": f"Bearer {commander_token}"}
    
    # 1. Welfare Officer records an intervention for P-000013
    int_payload = {
        "personnel_id": "P-000013",
        "intervention_type": "RECOVERY_LEAVE",
        "action_summary": "Granted 5 days restorative leave following cumulative night shifts surge"
    }
    int_res = requests.post(f"{BASE_URL}/api/v1/interventions/", json=int_payload, headers=welfare_headers)
    if int_res.status_code in [200, 201]:
        int_data = int_res.json()
        log_pass(f"Intervention recorded for P-000013 (ID: {int_data.get('intervention_id')})")
    else:
        log_fail(f"Failed to record intervention: {int_res.status_code} {int_res.text}")

    # 2. Commander initiates a monthly check-in follow-up
    fu_payload = {
        "notes": "Routine monthly welfare survey follow-up reminder"
    }
    fu_post_res = requests.post(f"{BASE_URL}/api/v1/commander/pending-checkins/P-000013/follow-up", json=fu_payload, headers=commander_headers)
    if fu_post_res.status_code in [200, 201]:
        log_pass("Commander successfully initiated monthly check-in follow-up")
    else:
        log_fail(f"Failed to create follow-up: {fu_post_res.status_code} {fu_post_res.text}")

    # 3. Check pending check-ins
    pending_res = requests.get(f"{BASE_URL}/api/v1/commander/pending-checkins", headers=commander_headers)
    if pending_res.status_code == 200:
        pending_data = pending_res.json()
        assert "items" in pending_data
        log_pass(f"Monthly check-in follow-up items retrieved: {len(pending_data['items'])} items")
    else:
        log_fail(f"Failed to fetch pending check-ins: {pending_res.status_code} {pending_res.text}")

if __name__ == "__main__":
    print("============================================================")
    print("   SAATHI SYSTEM VERIFICATION & READINESS AUDIT")
    print("============================================================")
    test_health()
    tokens = test_demo_accounts()
    test_personnel_records(tokens["welfare_officer"])
    test_ml_inference(tokens["welfare_officer"])
    test_wellness_companion(tokens["personnel_p13"], tokens["welfare_officer"])
    test_commander_portal(tokens["commander"])
    test_analyst_portal(tokens["analyst"])
    test_admin_portal(tokens["admin"])
    test_monthly_checkin_followup(tokens["welfare_officer"], tokens["commander"])
    print("\n============================================================")
    print("   ALL READINESS CHECKS PASSED PERFECTLY!")
    print("============================================================")
