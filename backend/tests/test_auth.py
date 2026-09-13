"""
SAATHI Authentication & Token Tests
"""

import pytest
from fastapi.testclient import TestClient

def test_login_success(client: TestClient):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_user", "password": "password123"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "admin_user"
    assert data["user"]["role"] == "ADMIN"

def test_login_invalid_password(client: TestClient):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_user", "password": "wrong_password"}
    )
    assert resp.status_code == 401
    assert "Incorrect username or password" in resp.json()["detail"]

def test_login_nonexistent_user(client: TestClient):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "ghost_user", "password": "password123"}
    )
    assert resp.status_code == 401

def test_get_current_user_profile(client: TestClient, welfare_token: str):
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {welfare_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "welfare_user"
    assert data["role"] == "WELFARE_OFFICER"
    assert "predictions:read" in data["permissions"]
    assert "interventions:write" in data["permissions"]

def test_expired_or_malformed_token(client: TestClient):
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_gibberish_token_value"}
    )
    assert resp.status_code == 401

def test_passlib_bcrypt_hash_and_verify_compatibility():
    """
    Render Deployment Regression: Verify passlib CryptContext and bcrypt
    hashing and verification initialize and execute without ValueError or backend errors.
    """
    from backend.app.core.security import get_password_hash, verify_password, pwd_context
    raw_pwd = "WelfareSecurePassword@123!"
    hashed = get_password_hash(raw_pwd)
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword@123", hashed) is False

def test_demo_roles_authentication_matrix(client: TestClient):
    """
    Verify all 5 institutional roles can authenticate with valid credentials.
    """
    credentials = [
        ("admin_user", "password123", "ADMIN"),
        ("welfare_user", "password123", "WELFARE_OFFICER"),
        ("commander_user", "password123", "COMMANDER"),
        ("analyst_user", "password123", "ANALYST"),
        ("personnel_p1", "password123", "PERSONNEL"),
        ("personnel_p2", "password123", "PERSONNEL"),
    ]
    for uname, pwd, expected_role in credentials:
        resp = client.post("/api/v1/auth/login", json={"username": uname, "password": pwd})
        assert resp.status_code == 200, f"Failed to login for {uname} with password {pwd}"
        data = resp.json()
        assert data["user"]["role"] == expected_role
        assert "access_token" in data


