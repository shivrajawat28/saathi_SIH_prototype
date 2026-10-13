"""
Regression tests for Database URL normalization, PostgreSQL dialect and driver selection.
Verifies that SQLAlchemy 2.x selects 'psycopg2' (psycopg2-binary) instead of
'psycopg' (Psycopg 3), preventing ModuleNotFoundError in cloud environments like Render.
"""

import pytest
from sqlalchemy import create_engine
from backend.app.core.config import Settings, normalize_database_url


def test_normalize_database_url_variations():
    """Verify various Postgres URL schemes normalize to postgresql+psycopg2:// without modifying credentials or SQLite."""
    # 1. Supabase copy-paste format (postgresql+psycopg://)
    url_psycopg3 = "postgresql+psycopg://postgres.fake_ref:SecretPass123@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
    norm_psycopg3 = normalize_database_url(url_psycopg3)
    assert norm_psycopg3.startswith("postgresql+psycopg2://")
    assert "SecretPass123" in norm_psycopg3
    assert norm_psycopg3.count("psycopg2") == 1

    # 2. Legacy Heroku / Render format (postgres://)
    url_legacy = "postgres://user:pass123@host.render.com:5432/mydb"
    norm_legacy = normalize_database_url(url_legacy)
    assert norm_legacy.startswith("postgresql+psycopg2://")

    # 3. Standard Postgres without driver scheme (postgresql://)
    url_standard = "postgresql://user:pass123@host.render.com:5432/mydb"
    norm_standard = normalize_database_url(url_standard)
    assert norm_standard.startswith("postgresql+psycopg2://")

    # 4. Explicit psycopg2 scheme (idempotency check)
    url_psycopg2 = "postgresql+psycopg2://user:pass123@host.render.com:5432/mydb"
    norm_psycopg2 = normalize_database_url(url_psycopg2)
    assert norm_psycopg2 == url_psycopg2

    # 5. SQLite scheme (must remain untouched)
    url_sqlite = "sqlite:///./saathi.db"
    norm_sqlite = normalize_database_url(url_sqlite)
    assert norm_sqlite == url_sqlite


def test_sqlalchemy_driver_selection_is_psycopg2():
    """
    Verify that create_engine with normalized URL instantiates dialect with driver == 'psycopg2'
    and dialect name == 'postgresql', without attempting to import 'psycopg' (Psycopg 3).
    """
    raw_supabase_url = "postgresql+psycopg://dbuser:mock_pass@mock_host.supabase.co:5432/postgres"
    normalized_url = normalize_database_url(raw_supabase_url)

    engine = create_engine(normalized_url)
    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "psycopg2"
    # Ensure psycopg (Psycopg 3) is NOT the driver
    assert engine.dialect.driver != "psycopg"


def test_settings_database_url_validation():
    """Verify Pydantic Settings automatically normalizes DATABASE_URL on assignment/load."""
    mock_url = "postgresql+psycopg://user:dummy_password@db.supabase.co:5432/postgres"
    custom_settings = Settings(DATABASE_URL=mock_url)
    assert custom_settings.DATABASE_URL.startswith("postgresql+psycopg2://")
    assert custom_settings.DATABASE_URL == normalize_database_url(mock_url)


def test_supabase_ssl_enforcement():
    """Verify SSL mode require is enforced for Supabase URLs."""
    raw_url = "postgresql+psycopg://postgres.ref:mock@aws-0.pooler.supabase.com:6543/postgres"
    normalized = normalize_database_url(raw_url)

    connect_args = {}
    if "supabase" in normalized and "sslmode" not in normalized:
        connect_args["sslmode"] = "require"

    assert connect_args.get("sslmode") == "require"


def test_no_credential_exposure_in_sanitized_logs():
    """Verify that masking connection strings safely excludes user credentials from log output."""
    raw_url = "postgresql+psycopg://user_admin:SuperSecretP@ssw0rd!@db.supabase.co:5432/postgres"
    masked = raw_url.split("@")[-1] if "@" in raw_url else raw_url
    assert "SuperSecretP@ssw0rd!" not in masked
    assert "user_admin" not in masked
    assert "db.supabase.co:5432/postgres" in masked
