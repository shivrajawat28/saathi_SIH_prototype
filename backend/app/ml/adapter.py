"""
SAATHI ML Adapter Module
Seamlessly interfaces the backend application with the locked Random Forest model,
personal baseline engine, and explainability service without duplicating or altering ML logic.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from backend.app.core.config import settings
from ml.baseline.personal_baseline import PersonalBaselineEngine
from ml.explainability.explainer import WelfareExplainer, FACTOR_NAME_MAP
from ml.config import SUPPORT_PRIORITIES, SCORE_THRESHOLDS

KEY_SIGNALS = [
    'duty_hours', 'overtime_hours', 'night_shifts', 'rest_hours',
    'sleep_quality', 'fatigue_level', 'self_reported_strain', 'routine_deviation'
]

class MLAdapter:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLAdapter, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize(self):
        model_candidates = [
            Path(settings.MODEL_PATH),
            settings.BASE_DIR / "ml/models/support_priority_model.joblib",
            Path.cwd() / "ml/models/support_priority_model.joblib",
            Path(__file__).resolve().parents[3] / "ml/models/support_priority_model.joblib",
            Path(__file__).resolve().parents[4] / "ml/models/support_priority_model.joblib",
        ]
        model_path = next((p for p in model_candidates if p.exists()), None)
        if not model_path:
            raise FileNotFoundError("Locked ML model artifact support_priority_model.joblib not found.")

        meta_candidates = [
            Path(settings.METADATA_PATH),
            settings.BASE_DIR / "ml/models/model_metadata.json",
            Path.cwd() / "ml/models/model_metadata.json",
            Path(__file__).resolve().parents[3] / "ml/models/model_metadata.json",
            Path(__file__).resolve().parents[4] / "ml/models/model_metadata.json",
        ]
        meta_path = next((p for p in meta_candidates if p.exists()), None)
        if not meta_path:
            raise FileNotFoundError("Model metadata artifact model_metadata.json not found.")

        self.pipeline = joblib.load(model_path)
        with open(meta_path, "r") as f:
            self.metadata = json.load(f)

        self.baseline_engine = PersonalBaselineEngine(min_history_periods=3, window_size=4)
        self.explainer = WelfareExplainer()
        print(f"[✓] ML Adapter initialized with model: {self.metadata.get('model_name')}")

    def compute_data_completeness(self, observation: Dict[str, Any]) -> float:
        """Computes fraction of non-null key signals present in observation."""
        present = sum(1 for k in KEY_SIGNALS if k in observation and observation[k] is not None and not pd.isna(observation[k]))
        return round(present / len(KEY_SIGNALS), 2)

    def calculate_support_score(self, prob_high_risk: float) -> Tuple[float, str]:
        """Maps calibrated high-risk probability to 0-100 continuous score and priority tier."""
        score = round(float(np.clip(prob_high_risk * 100.0, 5.0, 98.0)), 1)
        if score < 30.0:
            priority = "GREEN"
        elif score < 55.0:
            priority = "YELLOW"
        elif score < 75.0:
            priority = "ORANGE"
        else:
            priority = "RED"
        return score, priority

    def calculate_prediction_reliability(self, prob_high_risk: float, completeness: float, baseline_avail: bool) -> float:
        """
        Calculates prediction reliability incorporating model sharpness,
        data completeness, and personal baseline maturity.
        """
        prob_lower = 1.0 - prob_high_risk
        max_p = max(prob_high_risk, prob_lower)
        
        # Scale with data completeness
        reliability = max_p * (0.60 + 0.40 * completeness)
        
        # Cold-start penalty if insufficient baseline history
        if not baseline_avail:
            reliability *= 0.85

        return round(float(np.clip(reliability, 0.10, 0.99)), 2)

    def predict_observation(
        self,
        observation_df: pd.DataFrame,
        operating_threshold: float = 0.50
    ) -> Dict[str, Any]:
        """
        Runs inference on an engineered observation row (containing baseline deviations).
        """
        pid = str(observation_df['personnel_id'].iloc[0]) if 'personnel_id' in observation_df.columns else "P-UNKNOWN"
        obs_dict = observation_df.iloc[0].to_dict()
        completeness = self.compute_data_completeness(obs_dict)
        baseline_avail = bool(observation_df['baseline_available'].iloc[0]) if 'baseline_available' in observation_df.columns else False

        # If data completeness is below 35%, return INSUFFICIENT_DATA
        if completeness < 0.35:
            return {
                "personnel_id": pid,
                "status": "INSUFFICIENT_DATA",
                "priority": "INSUFFICIENT_DATA",
                "support_score": None,
                "high_risk_probability": None,
                "prediction_reliability": 0.0,
                "data_completeness": completeness,
                "baseline_maturity_months": int(observation_df['history_periods_count'].iloc[0]) if 'history_periods_count' in observation_df.columns else 0,
                "operating_threshold": operating_threshold,
                "top_factors": [],
                "human_review_required": False,
                "message": "Telemetry signals are incomplete (completeness < 35%). Informal welfare check-in recommended."
            }

        # Model Inference
        # Get class probabilities
        probas = self.pipeline.predict_proba(observation_df)[0]
        # Classes: 0=GREEN, 1=YELLOW, 2=ORANGE, 3=RED
        # High-Risk probability = P(Orange) + P(Red)
        if len(probas) == 4:
            p_high_risk = float(probas[2] + probas[3])
        elif len(probas) == 2:
            p_high_risk = float(probas[1])
        else:
            p_high_risk = float(probas[0])

        score, priority = self.calculate_support_score(p_high_risk)
        reliability = self.calculate_prediction_reliability(p_high_risk, completeness, baseline_avail)
        human_review = bool(p_high_risk >= operating_threshold or score >= 55.0)

        # Factor Attribution
        top_factors = self.explainer.explain_instance(observation_df, top_k=3)

        return {
            "personnel_id": pid,
            "status": "VALID",
            "priority": priority,
            "support_score": score,
            "high_risk_probability": round(p_high_risk, 4),
            "prediction_reliability": reliability,
            "data_completeness": completeness,
            "baseline_maturity_months": int(observation_df['history_periods_count'].iloc[0]) if 'history_periods_count' in observation_df.columns else 4,
            "operating_threshold": operating_threshold,
            "top_factors": top_factors,
            "human_review_required": human_review,
            "message": None
        }

ml_adapter = MLAdapter()
