"""
SAATHI Prediction & Decision Support Database Models
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(64), unique=True, index=True, nullable=False)
    personnel_id = Column(String(32), ForeignKey("personnel.personnel_id", ondelete="CASCADE"), index=True, nullable=False)
    prediction_month_idx = Column(Integer, nullable=False)
    
    support_score = Column(Float, nullable=True) # 0-100
    support_priority = Column(String(16), nullable=False) # GREEN, YELLOW, ORANGE, RED, INSUFFICIENT_DATA
    high_risk_probability = Column(Float, nullable=True) # 0-1
    prediction_reliability = Column(Float, nullable=False) # 0-1
    data_completeness = Column(Float, nullable=False) # 0-1
    baseline_maturity_months = Column(Integer, nullable=False)
    operating_threshold = Column(Float, default=0.50)
    human_review_required = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    personnel = relationship("Personnel", back_populates="predictions")
    explanations = relationship("PredictionExplanation", back_populates="prediction", cascade="all, delete-orphan")
    recommendations = relationship("WelfareRecommendation", back_populates="prediction", cascade="all, delete-orphan")

class PredictionExplanation(Base):
    __tablename__ = "prediction_explanations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(64), ForeignKey("predictions.prediction_id", ondelete="CASCADE"), index=True, nullable=False)
    factor_name = Column(String(128), nullable=False)
    direction = Column(String(16), nullable=False) # increase, decrease
    contribution_score = Column(Float, nullable=False)

    prediction = relationship("Prediction", back_populates="explanations")

class WelfareRecommendation(Base):
    __tablename__ = "welfare_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(64), ForeignKey("predictions.prediction_id", ondelete="CASCADE"), index=True, nullable=False)
    recommendation_type = Column(String(64), nullable=False) # WORKLOAD_REVIEW, RECOVERY_LEAVE, WELFARE_CHECK_IN, etc.
    priority_level = Column(String(16), nullable=False) # LOW, MEDIUM, HIGH
    reason = Column(Text, nullable=False)

    prediction = relationship("Prediction", back_populates="recommendations")
