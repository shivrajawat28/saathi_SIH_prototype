"""
SAATHI Personnel & HR Profile Database Models
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Personnel(Base):
    __tablename__ = "personnel"

    personnel_id = Column(String(32), primary_key=True, index=True) # P-000001
    original_ref_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    hr_profile = relationship("HRProfile", back_populates="personnel", uselist=False, cascade="all, delete-orphan")
    workload_records = relationship("WorkloadRecord", back_populates="personnel", cascade="all, delete-orphan")
    leave_records = relationship("LeaveRecord", back_populates="personnel", cascade="all, delete-orphan")
    deployment_records = relationship("DeploymentRecord", back_populates="personnel", cascade="all, delete-orphan")
    wellness_records = relationship("WellnessRecord", back_populates="personnel", cascade="all, delete-orphan")
    behavioral_records = relationship("BehavioralRecord", back_populates="personnel", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="personnel", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="personnel", cascade="all, delete-orphan")
    wellness_conversations = relationship("WellnessConversation", back_populates="personnel", cascade="all, delete-orphan")

class HRProfile(Base):
    __tablename__ = "hr_profiles"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    age = Column(Integer, nullable=True)
    gender = Column(String(16), nullable=True)
    department = Column(String(64), nullable=True, index=True)
    job_role = Column(String(64), nullable=True, index=True)
    job_level = Column(Integer, nullable=True, index=True)
    education_level = Column(Integer, nullable=True)
    education_field = Column(String(64), nullable=True)
    marital_status = Column(String(32), nullable=True)
    distance_from_home = Column(Integer, nullable=True)
    business_travel = Column(String(32), nullable=True)
    overtime_eligible = Column(String(8), nullable=True)
    total_working_years = Column(Integer, nullable=True)
    years_in_service = Column(Integer, nullable=True)
    years_in_current_role = Column(Integer, nullable=True)
    years_since_last_promotion = Column(Integer, nullable=True)
    years_with_curr_supervisor = Column(Float, nullable=True)
    
    baseline_env_satisfaction = Column(Integer, nullable=True)
    baseline_job_satisfaction = Column(Integer, nullable=True)
    baseline_job_involvement = Column(Integer, nullable=True)
    baseline_work_life_balance = Column(Integer, nullable=True)
    baseline_rel_satisfaction = Column(Integer, nullable=True)
    performance_rating = Column(Integer, nullable=True)
    training_times_last_year = Column(Integer, nullable=True)
    monthly_income = Column(Integer, nullable=True)

    personnel = relationship("Personnel", back_populates="hr_profile")
