"""
SAATHI Backend Pytest Fixtures & Test Setup
"""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set testing environment before importing app
os.environ["SECRET_KEY"] = "test_super_secret_jwt_key_saathi_2026_secure"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from backend.app.db.session import Base, get_db
from backend.app.main import app
from backend.app.models.user import User, Role
from backend.app.models.personnel import Personnel, HRProfile
from backend.app.core.security import get_password_hash, create_access_token

# Test in-memory SQLite database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed roles
    roles = {
        "ADMIN": Role(name="ADMIN", description="Admin"),
        "WELFARE_OFFICER": Role(name="WELFARE_OFFICER", description="Welfare Officer"),
        "COMMANDER": Role(name="COMMANDER", description="Commander"),
        "ANALYST": Role(name="ANALYST", description="Analyst"),
        "PERSONNEL": Role(name="PERSONNEL", description="Personnel")
    }
    for r in roles.values():
        db.add(r)
    db.commit()

    # Seed sample personnel
    p1 = Personnel(personnel_id="P-000001", original_ref_id="REF-1")
    p1.hr_profile = HRProfile(
        personnel_id="P-000001",
        age=35,
        department="Operations",
        job_role="Field Specialist",
        job_level=2,
        years_in_service=7
    )
    p2 = Personnel(personnel_id="P-000002", original_ref_id="REF-2")
    p2.hr_profile = HRProfile(
        personnel_id="P-000002",
        age=28,
        department="Communications & Technology",
        job_role="Signals & Comms Technician",
        job_level=1,
        years_in_service=3
    )
    p13 = Personnel(personnel_id="P-000013", original_ref_id="REF-13")
    p13.hr_profile = HRProfile(
        personnel_id="P-000013",
        age=32,
        department="Communications & Technology",
        job_role="Technical Specialist",
        job_level=2,
        years_in_service=5
    )
    p81 = Personnel(personnel_id="P-000081", original_ref_id="REF-81")
    p81.hr_profile = HRProfile(
        personnel_id="P-000081",
        age=40,
        department="Operations",
        job_role="Field Sub-Inspector",
        job_level=3,
        years_in_service=10
    )
    db.add(p1)
    db.add(p2)
    db.add(p13)
    db.add(p81)
    db.commit()

    # Seed users
    users = [
        ("admin_user", "admin@test.gov", "ADMIN", None),
        ("welfare_user", "welfare@test.gov", "WELFARE_OFFICER", None),
        ("commander_user", "commander@test.gov", "COMMANDER", None),
        ("analyst_user", "analyst@test.gov", "ANALYST", None),
        ("personnel_p1", "p1@test.gov", "PERSONNEL", "P-000001"),
        ("personnel_p2", "p2@test.gov", "PERSONNEL", "P-000002")
    ]
    for uname, email, rname, pid in users:
        u = User(
            username=uname,
            email=email,
            hashed_password=get_password_hash("password123"),
            full_name=uname.replace("_", " ").title(),
            personnel_id=pid,
            is_active=True
        )
        u.roles.append(roles[rname])
        db.add(u)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def admin_token():
    return create_access_token(subject="admin_user", role="ADMIN")

@pytest.fixture
def welfare_token():
    return create_access_token(subject="welfare_user", role="WELFARE_OFFICER")

@pytest.fixture
def commander_token():
    return create_access_token(subject="commander_user", role="COMMANDER")

@pytest.fixture
def analyst_token():
    return create_access_token(subject="analyst_user", role="ANALYST")

@pytest.fixture
def personnel_p1_token():
    return create_access_token(subject="personnel_p1", role="PERSONNEL")

@pytest.fixture
def personnel_token():
    return create_access_token(subject="personnel_p1", role="PERSONNEL")

@pytest.fixture
def personnel_p2_token():
    return create_access_token(subject="personnel_p2", role="PERSONNEL")
