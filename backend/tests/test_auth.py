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
