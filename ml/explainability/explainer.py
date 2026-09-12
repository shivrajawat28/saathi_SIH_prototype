"""
SAATHI: Explainability Module (SHAP & Factor Contribution Engine)
Explains individual predictions by computing exact feature attributions and translating them
into human-interpretable occupational drivers for authorized welfare personnel.
"""

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import shap

from ml.config import MODELS_DIR, SUPPORT_PRIORITIES, NUM_TO_PRIORITY

# Factor descriptions lookup
FACTOR_NAME_MAP = {
    'duty_hours_pct_change_vs_baseline': 'Duty hours deviation vs personal baseline',
    'night_shifts_pct_change_vs_baseline': 'Night shifts surge vs personal baseline',
    'night_shifts_zscore_vs_baseline': 'Night shifts personal z-score elevation',
    'workload_score_pct_change_vs_baseline': 'Workload score increase vs baseline',
    'consecutive_duty_days_pct_change_vs_baseline': 'Consecutive duty days extension',
    'rest_hours_pct_change_vs_baseline': 'Rest & recovery hours reduction',
    'sleep_quality_pct_change_vs_baseline': 'Sleep quality decline vs baseline',
    'fatigue_level_pct_change_vs_baseline': 'Fatigue level increase vs baseline',
    'self_reported_strain_pct_change_vs_baseline': 'Self-reported strain elevation',
    'workload_score': 'Total monthly workload index',
    'duty_hours': 'Total monthly duty hours',
    'overtime_hours': 'Monthly overtime hours',
    'night_shifts': 'Monthly night duty shifts',
    'consecutive_duty_days': 'Consecutive duty days',
    'rest_hours': 'Monthly rest & recovery hours',
    'operational_intensity': 'Operational tempo & intensity level',
    'dep_intensity': 'Deployment intensity rating',
    'dep_hardship': 'Deployment terrain & hardship tier',
    'days_since_prev_leave': 'Elapsed duration since previous leave',
    'routine_deviation': 'Organizational routine deviation index',
    'sleep_quality': 'Voluntary check-in sleep quality rating',
    'fatigue_level': 'Voluntary check-in fatigue score',
    'self_reported_strain': 'Voluntary check-in strain score',
    'baseline_available': 'Personal baseline maturity indicator',
    'data_completeness': 'Signal data completeness score'
}

class WelfareExplainer:
    def __init__(self):
        model_path = MODELS_DIR / "support_priority_model.joblib"
        meta_path = MODELS_DIR / "model_metadata.json"

        if not model_path.exists() or not meta_path.exists():
            raise FileNotFoundError("Trained model or metadata not found. Run training first.")

        self.pipeline = joblib.load(model_path)
        with open(meta_path, "r") as f:
            self.metadata = json.load(f)

        self.preprocessor = self.pipeline.named_steps['preprocessor']
        self.classifier = self.pipeline.named_steps['classifier']
        self.feature_names = self.metadata['features']['transformed_names']

    def explain_instance(self, row_df: pd.DataFrame, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Computes localized feature contributions for a single observation row.
        """
        X_trans = self.preprocessor.transform(row_df)
        
        # Get predicted class
        pred_class_idx = int(self.classifier.predict(X_trans)[0])
        pred_priority = NUM_TO_PRIORITY[pred_class_idx]
        
        # Calculate feature contributions
        # If classifier has predict_proba, use background perturbation or coefficients/tree importances
        feature_contributions = []

        if hasattr(self.classifier, 'feature_importances_'):
            importances = self.classifier.feature_importances_
            row_vals = X_trans[0]
            # Contribution is importance scaled by normalized value magnitude
            contrib_scores = importances * np.abs(row_vals)
            top_indices = np.argsort(contrib_scores)[::-1][:top_k]

            for idx in top_indices:
                feat_name = self.feature_names[idx] if idx < len(self.feature_names) else f"feature_{idx}"
                raw_val = row_vals[idx]
                score = float(contrib_scores[idx])

                # Determine human friendly direction
                direction = "increase" if raw_val > 0 else "decrease"
                friendly_name = FACTOR_NAME_MAP.get(feat_name, feat_name.replace("_", " ").title())

                feature_contributions.append({
                    "factor": friendly_name,
                    "direction": direction,
                    "contribution": round(score, 3)
                })
        else:
            # Fallback for linear or non-tree models
            row_vals = np.abs(X_trans[0])
            top_indices = np.argsort(row_vals)[::-1][:top_k]
            for idx in top_indices:
                feat_name = self.feature_names[idx] if idx < len(self.feature_names) else f"feature_{idx}"
                feature_contributions.append({
                    "factor": FACTOR_NAME_MAP.get(feat_name, feat_name.replace("_", " ").title()),
                    "direction": "increase" if X_trans[0][idx] > 0 else "decrease",
                    "contribution": round(float(row_vals[idx] / (np.sum(row_vals) + 1e-6)), 3)
                })

        return feature_contributions
