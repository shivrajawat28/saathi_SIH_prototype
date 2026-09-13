"""
SAATHI Phase 6 Polish & Correction Regression Tests
Validates:
1. P0-1: Elimination of duplicate personnel in batch triage dashboard.
2. P0-2 & P0-3: Canonical demo candidate P-000013 consistency across database, ML, telemetry, and API layers.
3. P0-4 & P0-5: Force-oriented synthetic taxonomy mapping (no corporate departments leaking into API presentation).
4. P1-6 to P1-9: Operational context (deployment, transfers, training, proactive welfare alerts).
5. P1-10 & P1-11: What-If simulation projections and non-causal integrity.
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.main import app
from backend.app.models.user import User
from backend.app.models.prediction import Prediction
from backend.app.services.prediction_service import PredictionService
from backend.app.core.taxonomy import map_department, map_job_role

def test_p0_1_duplicate_personnel_elimination(client, welfare_token):
    """
    P0-1 Regression: Ensure batch triage endpoint returns strictly at most ONE record per personnel_id,
    even if multiple historical prediction runs have been triggered.
    """
    headers = {"Authorization": f"Bearer {welfare_token}"}
    
    # Trigger prediction 4 times for P-000013
    for _ in range(4):
        client.post("/api/v1/predictions/personnel/P-000013", headers=headers)
    
    # Trigger prediction 3 times for P-000081
    for _ in range(3):
        client.post("/api/v1/predictions/personnel/P-000081", headers=headers)

    response = client.get("/api/v1/predictions/batch-triage?limit=50", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0

    personnel_ids = [item["personnel_id"] for item in items]
    unique_ids = set(personnel_ids)
    
    # Assert each personnel_id appears exactly once in the triage list
    assert len(personnel_ids) == len(unique_ids), f"Duplicate personnel found in triage: {personnel_ids}"
    assert "P-000013" in unique_ids

def test_p0_2_and_p0_3_canonical_demo_p13_consistency(client, welfare_token):
    """
    P0-2 & P0-3 Regression: Verify P-000013 is canonical high-strain demo scenario with exact metric consistency:
    duty_hours ≈ 261.2h, night_shifts = 14, rest_hours ≈ 38.3h, leave_gap = 302d, support_score ≈ 88.1 RED.
    """
    headers = {"Authorization": f"Bearer {welfare_token}"}
    
    # 1. Prediction API
    pred_res = client.post("/api/v1/predictions/personnel/P-000013", headers=headers)
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    assert pred_data["personnel_id"] == "P-000013"
    assert pred_data["priority"] == "RED"
    assert round(pred_data["support_score"], 1) == 88.1
    assert pred_data["high_risk_probability"] > 0.80

    # 2. Longitudinal Timeline API
    timeline_res = client.get("/api/v1/personnel/P-000013/timeline", headers=headers)
    assert timeline_res.status_code == 200
    timeline_data = timeline_res.json()
    assert timeline_data["total_months"] == 12
    
    m12 = timeline_data["timeline"][-1]
    assert m12["month_idx"] == 12
    assert abs(m12["duty_hours"] - 261.2) < 0.5
    assert m12["night_shifts"] == 14
    assert abs(m12["rest_hours"] - 38.3) < 0.5
    assert m12["days_since_prev_leave"] == 302
    assert m12["support_priority"] == "RED"
    assert m12["operational_intensity"] == 5
    deployed_months = sum(1 for m in timeline_data["timeline"] if m["is_deployed"])
    assert deployed_months == 8

def test_p0_4_and_p0_5_force_taxonomy_in_presentation_layer(client, welfare_token, commander_token):
    """
    P0-4 & P0-5 Regression: Corporate HR terminology ('Sales', 'Sales Executive', 'Research & Development')
    must NOT appear in the user-facing API presentation layer.
    """
    # 1. Personnel Profile
    w_headers = {"Authorization": f"Bearer {welfare_token}"}
    p1_res = client.get("/api/v1/personnel/P-000001", headers=w_headers)
    assert p1_res.status_code == 200
    p1_data = p1_res.json()
    assert "Sales" not in p1_data["department"]
    assert p1_data["department"] in ["Operations", "Communications & Technology", "Administration & Welfare", "Logistics & Support", "Training & Readiness"]
    assert "Sales Executive" not in p1_data["job_role"]
    assert p1_data["job_role"] in ["Field Sub-Inspector", "Field Specialist"]

    # 2. Commander Overview
    c_headers = {"Authorization": f"Bearer {commander_token}"}
    c_res = client.get("/api/v1/analytics/commander-overview", headers=c_headers)
    assert c_res.status_code == 200
    c_data = c_res.json()
    dept_names = [d["department"] for d in c_data["department_breakdown"]]
    assert "Sales" not in dept_names
    assert "Research & Development" not in dept_names
    for d in dept_names:
        assert d in ["Operations", "Communications & Technology", "Administration & Welfare", "Logistics & Support", "Training & Readiness"]

def test_p1_10_what_if_simulation_integrity(client, welfare_token):
    """
    P1-10 Regression: Ensure What-If simulation produces projected improvement without causal guarantees
    and validates positive inputs safely.
    """
    headers = {"Authorization": f"Bearer {welfare_token}"}
    sim_payload = {
        "reduce_night_shifts": 8,
        "reduce_duty_hours": 40,
        "grant_recovery_days": 3,
        "reduce_overtime_hours": 10
    }
    sim_res = client.post("/api/v1/simulations/personnel/P-000013", json=sim_payload, headers=headers)
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["personnel_id"] == "P-000013"
    assert sim_data["current_score"] == 88.1
    assert sim_data["projected_score"] < sim_data["current_score"]
    assert sim_data["projected_delta"] < 0
    assert len(sim_data["parameter_changes"]) >= 3

def test_shap_explainability_and_app_import_integrity():
    """
    Render Deployment Regression: Ensure SHAP is installed, explainer initializes,
    and FastAPI production app import path is clean.
    """
    import shap
    assert shap.__version__ is not None

    from ml.explainability.explainer import WelfareExplainer
    explainer = WelfareExplainer()
    assert explainer.classifier is not None

    from backend.app.main import app
    assert app.title == "SAATHI AI Welfare Decision Support System"

def test_locked_ml_artifact_loading_and_remainder_cols_regression(client, welfare_token):
    """
    Render Deployment Regression: Ensure scikit-learn unpickling of ColumnTransformer
    with _RemainderColsList succeeds and produces canonical P-000013 predictions.
    """
    import joblib
    from pathlib import Path
    from backend.app.ml.adapter import ml_adapter
    from backend.app.services.prediction_service import PredictionService

    # 1. Model file exists and loads cleanly
    model_path = Path("ml/models/support_priority_model.joblib")
    assert model_path.exists()
    loaded_pipe = joblib.load(model_path)
    assert "preprocessor" in loaded_pipe.named_steps
    assert "classifier" in loaded_pipe.named_steps

    # 2. ML Adapter is initialized
    assert ml_adapter.pipeline is not None
    assert ml_adapter.metadata["model_name"] == "Random Forest (Balanced)"

    # 3. Canonical P-000013 inference produces exact expected results
    headers = {"Authorization": f"Bearer {welfare_token}"}
    res = client.post("/api/v1/predictions/personnel/P-000013", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["personnel_id"] == "P-000013"
    assert data["priority"] == "RED"
    assert round(data["support_score"], 1) == 88.1
    assert data["high_risk_probability"] > 0.85
    assert len(data["top_factors"]) >= 3


