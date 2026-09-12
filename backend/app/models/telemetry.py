"""
SAATHI Longitudinal Telemetry Database Models
Covers deployment, leave, workload, voluntary wellness, and behavioral change indicators.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class DeploymentRecord(Base):
    __tablename__ = "deployment_records"

    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(String(32), unique=True, index=True, nullable=False)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), index=True, nullable=False)
    month_idx = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    deployment_duration_days = Column(Integer, nullable=False)
    deployment_type = Column(String(32), nullable=False)
    operational_intensity = Column(Integer, nullable=False)
    hardship_level = Column(Integer, nullable=False)
    recovery_required = Column(Boolean, default=False)
    location_category = Column(String(64), nullable=False)

    personnel = relationship("Personnel", back_populates="deployment_records")

class LeaveRecord(Base):
    __tablename__ = "leave_records"

    id = Column(Integer, primary_key=True, index=True)
    leave_id = Column(String(32), unique=True, index=True, nullable=False)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), index=True, nullable=False)
    month_idx = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    leave_start_date = Column(Date, nullable=False)
    leave_end_date = Column(Date, nullable=False)
    duration_days = Column(Integer, nullable=False)
    leave_type = Column(String(32), nullable=False)
    days_since_previous_leave = Column(Integer, nullable=False)

    personnel = relationship("Personnel", back_populates="leave_records")

class WorkloadRecord(Base):
    __tablename__ = "workload_records"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), index=True, nullable=False)
    month_idx = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    duty_hours = Column(Float, nullable=False)
    overtime_hours = Column(Float, nullable=False)
    night_shifts = Column(Integer, nullable=False)
    consecutive_duty_days = Column(Integer, nullable=False)
    rest_hours = Column(Float, nullable=False)
    workload_score = Column(Float, nullable=False)
    operational_intensity = Column(Integer, nullable=False)
    schedule_irregularity = Column(Float, nullable=False)

    personnel = relationship("Personnel", back_populates="workload_records")

class WellnessRecord(Base):
    __tablename__ = "wellness_records"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), index=True, nullable=False)
    month_idx = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    sleep_quality = Column(Float, nullable=True) # 1-5
    fatigue_level = Column(Float, nullable=True) # 1-5
    work_stress = Column(Float, nullable=True) # 1-5
    mood_wellbeing = Column(Float, nullable=True) # 1-5
    work_life_balance = Column(Float, nullable=True) # 1-5
    job_satisfaction = Column(Float, nullable=True) # 1-5
    recovery_quality = Column(Float, nullable=True) # 1-5
    self_reported_strain = Column(Float, nullable=True) # 1-5
    checkin_completion = Column(Boolean, default=True)

    personnel = relationship("Personnel", back_populates="wellness_records")

class BehavioralRecord(Base):
    __tablename__ = "behavioral_records"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), index=True, nullable=False)
    month_idx = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    attendance_change = Column(Float, nullable=False)
    leave_frequency_change = Column(Float, nullable=False)
    workload_change = Column(Float, nullable=False)
    sleep_change = Column(Float, nullable=False)
    routine_deviation = Column(Float, nullable=False)
    performance_change = Column(Float, nullable=False)
    schedule_change = Column(Float, nullable=False)
    recovery_change = Column(Float, nullable=False)

    personnel = relationship("Personnel", back_populates="behavioral_records")
