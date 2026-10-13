"""
SAATHI Database Session & Engine Configuration (SQLAlchemy 2.x)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings, normalize_database_url

db_url = normalize_database_url(settings.DATABASE_URL)

# Handle SQLite vs PostgreSQL arguments
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    if "supabase" in db_url and "sslmode" not in db_url:
        connect_args["sslmode"] = "require"
    engine_kwargs.update({
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_engine(
    db_url,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency providing a transactional database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
