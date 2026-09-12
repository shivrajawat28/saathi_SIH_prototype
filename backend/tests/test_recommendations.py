"""
SAATHI Deterministic Welfare Recommendation Engine Tests
"""

import pytest
from backend.app.services.recommendation_service import RecommendationService

def test_insufficient_data_recommendation():
    recs = RecommendationService.generate_recommendations(
        priority="INSUFFICIENT_DATA",
        support_score=0.0,
        top_factors=[],
        observation={}
    )
    assert len(recs) == 1
    assert recs[0]["type"] == "WELFARE_CHECK_IN"
    assert "incomplete" in recs[0]["reason"].lower()

def test_recovery_leave_recommendation_trigger():
    obs = {"days_since_prev_leave": 130, "duty_hours": 160, "night_shifts": 2}
    recs = RecommendationService.generate_recommendations(
        priority="ORANGE",
        support_score=68.5,
        top_factors=[{"factor": "Elapsed duration since previous leave", "direction": "decrease", "contribution": 0.08}],
        observation=obs
    )
    types = [r["type"] for r in recs]
    assert "RECOVERY_LEAVE" in types
    assert "WELFARE_CHECK_IN" in types

def test_workload_review_recommendation_trigger():
    obs = {"days_since_prev_leave": 20, "duty_hours": 240, "night_shifts": 8}
    recs = RecommendationService.generate_recommendations(
        priority="RED",
        support_score=82.0,
        top_factors=[{"factor": "Night shifts surge vs personal baseline", "direction": "increase", "contribution": 0.12}],
        observation=obs
    )
    types = [r["type"] for r in recs]
    assert "WORKLOAD_REVIEW" in types
    assert "FOLLOW_UP_ASSESSMENT" in types
    assert "WELFARE_CHECK_IN" in types

def test_routine_monitoring_for_green_no_triggers():
    obs = {"days_since_prev_leave": 20, "duty_hours": 150, "night_shifts": 1}
    recs = RecommendationService.generate_recommendations(
        priority="GREEN",
        support_score=14.0,
        top_factors=[],
        observation=obs
    )
    assert len(recs) == 1
    assert recs[0]["type"] == "ROUTINE_MONITORING"
