"""
SAATHI: Safe Prediction & Welfare Support Priority Service
Generates structured, ethical welfare review predictions with confidence, data completeness,
baseline indicators, and factor attribution.
"""

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Union, List

from ml.config import (
    MODELS_DIR,
    PROCESSED_DIR,
    SUPPORT_PRIORITIES,
    NUM_TO_PRIORITY,
    PRIORITY_DESCRIPTIONS
)
from ml.explainability.explainer import WelfareExplainer

class WelfarePredictionService:
    def __init__(self):
        model_path = MODELS_DIR / "support_priority_model.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {model_path}. Run training first.")
        
        self.pipeline = joblib.load(model_path)
        self.explainer = WelfareExplainer()

    def predict_personnel(self, record: Union[Dict[str, Any], pd.DataFrame]) -> Dict[str, Any]:
        """
        Runs safe inference on a single personnel monthly observation.
        """
        if isinstance(record, dict):
            df = pd.DataFrame([record])
        else:
            df = record.copy()

        pid = str(df['personnel_id'].iloc[0]) if 'personnel_id' in df.columns else "P-UNKNOWN"

        # 1. Data Completeness Check
        key_signals = [
            'duty_hours', 'overtime_hours', 'night_shifts', 'rest_hours',
            'sleep_quality', 'fatigue_level', 'self_reported_strain', 'routine_deviation'
        ]
        present_signals = [s for s in key_signals if s in df.columns and pd.notnull(df[s].iloc[0])]
        completeness = round(len(present_signals) / len(key_signals), 2)

        # Baseline availability check
        baseline_avail = bool(df['baseline_available'].iloc[0]) if 'baseline_available' in df.columns else False

        # If data is severely incomplete (<35%), return INSUFFICIENT_DATA status
        if completeness < 0.35:
            return {
                "personnel_id": pid,
                "status": "INSUFFICIENT_DATA",
                "support_priority": "INSUFFICIENT_DATA",
                "score": None,
                "confidence": 0.0,
                "data_completeness": completeness,
                "baseline_available": baseline_avail,
                "message": "Insufficient operational and voluntary wellness signals to establish a reliable welfare review.",
                "top_factors": []
            }

        # 2. Run Model Pipeline
        try:
            pred_class_idx = int(self.pipeline.predict(df)[0])
            pred_priority = NUM_TO_PRIORITY[pred_class_idx]
            
            # Predict Probabilities
            if hasattr(self.pipeline, "predict_proba"):
                probas = self.pipeline.predict_proba(df)[0]
                raw_conf = float(np.max(probas))
                # Weighted priority score (0-100) based on class probability distribution
                # Weights: GREEN=15, YELLOW=45, ORANGE=68, RED=90
                class_weights = np.array([15.0, 45.0, 68.0, 90.0])
                score = float(np.sum(probas * class_weights))
            else:
                raw_conf = 0.80
                score_map = {"GREEN": 20.0, "YELLOW": 45.0, "ORANGE": 65.0, "RED": 85.0}
                score = score_map.get(pred_priority, 50.0)

            # Calibrate confidence based on completeness and baseline maturity
            confidence = raw_conf * (0.6 + 0.4 * completeness)
            if not baseline_avail:
                confidence *= 0.85 # Mild penalty for cold-start without personal baseline

            confidence = round(float(np.clip(confidence, 0.1, 0.99)), 2)
            score = round(float(np.clip(score, 5.0, 98.0)), 1)

            # 3. Generate Local Factor Explanations
            top_factors = self.explainer.explain_instance(df, top_k=3)

            return {
                "personnel_id": pid,
                "status": "VALID",
                "support_priority": pred_priority,
                "score": score,
                "confidence": confidence,
                "data_completeness": completeness,
                "baseline_available": baseline_avail,
                "description": PRIORITY_DESCRIPTIONS.get(pred_priority, ""),
                "top_factors": top_factors,
                "ethical_guardrail": "Authorized decision support only. Identifies occupational welfare review priority; not a clinical assessment or punitive tool."
            }

        except Exception as e:
            return {
                "personnel_id": pid,
                "status": "ERROR",
                "support_priority": "ERROR",
                "error_message": str(e),
                "data_completeness": completeness,
                "baseline_available": baseline_avail
            }

def run_sample_predictions():
    """
    Demonstration CLI running inference on representative test records.
    """
    data_path = PROCESSED_DIR / "integrated_longitudinal.parquet"
    if not data_path.exists():
        data_path = PROCESSED_DIR / "integrated_longitudinal.csv"
        df = pd.read_csv(data_path)
    else:
        df = pd.read_parquet(data_path)

    service = WelfarePredictionService()

    # Pick 4 diverse sample personnel from test period (month 11)
    test_records = df[df['month_idx'] == 11].head(4)

    print("=" * 70)
    print("SAATHI INFERENCE & WELFARE PRIORITY DEMONSTRATION")
    print("=" * 70)

    for idx, (_, row) in enumerate(test_records.iterrows(), 1):
        row_df = pd.DataFrame([row])
        result = service.predict_personnel(row_df)
        print(f"\n--- Sample #{idx} ---")
        print(json.dumps(result, indent=2))

    # Test edge case: Missing data / Cold start
    print("\n--- Edge Case: Highly Incomplete Observation ---")
    incomplete_row = test_records.iloc[[0]].copy()
    for col in ['duty_hours', 'overtime_hours', 'night_shifts', 'rest_hours', 'sleep_quality', 'fatigue_level']:
        incomplete_row[col] = np.nan
    incomplete_result = service.predict_personnel(incomplete_row)
    print(json.dumps(incomplete_result, indent=2))

if __name__ == "__main__":
    run_sample_predictions()
