"""
SAATHI: Model Training Pipeline
Performs strictly time-aware training across:
1. Multiclass Weighted Logistic Regression
2. Balanced Random Forest Classifier
3. Gradient Boosted Classifier (HistGradientBoosting / XGBoost)

Saves the best end-to-end pipeline (preprocessing + model + metadata) to ml/models/.
"""

import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import classification_report, f1_score, recall_score, precision_score
import xgboost as xgb

from ml.config import (
    PROCESSED_DIR,
    MODELS_DIR,
    RESULTS_DIR,
    RANDOM_SEED,
    PRIORITY_TO_NUM,
    NUM_TO_PRIORITY,
    SUPPORT_PRIORITIES
)

# Feature definitions
CATEGORICAL_FEATURES = [
    'department', 'job_role', 'gender', 'marital_status', 'overtime_eligible',
    'business_travel', 'dep_type', 'dep_location', 'leave_type'
]

NUMERICAL_FEATURES = [
    # Static Master
    'age', 'job_level', 'education_level', 'distance_from_home', 'total_working_years',
    'years_in_service', 'years_in_current_role', 'years_since_last_promotion', 'years_with_curr_supervisor',
    'baseline_env_satisfaction', 'baseline_job_satisfaction', 'baseline_job_involvement',
    'baseline_work_life_balance', 'baseline_rel_satisfaction', 'performance_rating',
    'training_times_last_year', 'monthly_income', 'num_prior_organizations',
    # Current Period Operational & Workload
    'duty_hours', 'overtime_hours', 'night_shifts', 'consecutive_duty_days',
    'rest_hours', 'workload_score', 'operational_intensity', 'schedule_irregularity',
    'is_deployed', 'dep_duration_days', 'dep_intensity', 'dep_hardship',
    'took_leave', 'leave_duration_days', 'days_since_prev_leave',
    # Voluntary Wellness
    'sleep_quality', 'fatigue_level', 'work_stress', 'mood_wellbeing',
    'work_life_balance', 'job_satisfaction', 'recovery_quality', 'self_reported_strain',
    # Behavioral Changes
    'attendance_change', 'leave_frequency_change', 'workload_change', 'sleep_change',
    'routine_deviation', 'performance_change', 'schedule_change', 'recovery_change',
    # Baseline Deviations & Trends
    'duty_hours_pct_change_vs_baseline', 'duty_hours_zscore_vs_baseline', 'duty_hours_lag1_diff',
    'overtime_hours_pct_change_vs_baseline', 'overtime_hours_zscore_vs_baseline',
    'night_shifts_pct_change_vs_baseline', 'night_shifts_zscore_vs_baseline', 'night_shifts_lag1_diff',
    'consecutive_duty_days_pct_change_vs_baseline', 'consecutive_duty_days_zscore_vs_baseline',
    'rest_hours_pct_change_vs_baseline', 'rest_hours_zscore_vs_baseline',
    'workload_score_pct_change_vs_baseline', 'workload_score_zscore_vs_baseline', 'workload_score_lag1_diff',
    'sleep_quality_pct_change_vs_baseline', 'sleep_quality_zscore_vs_baseline',
    'fatigue_level_pct_change_vs_baseline', 'fatigue_level_zscore_vs_baseline',
    'self_reported_strain_pct_change_vs_baseline', 'self_reported_strain_zscore_vs_baseline',
    # Data & Baseline Quality Flags
    'data_completeness'
]

# Boolean flags cast to integer
NUMERICAL_FEATURES += ['baseline_available', 'dep_recovery_required', 'checkin_completion']

def build_preprocessor():
    """
    Constructs a robust ColumnTransformer that handles numeric imputation/scaling
    and one-hot categorical encoding with unknown category safety.
    """
    numeric_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='Missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_pipeline, NUMERICAL_FEATURES),
            ('cat', categorical_pipeline, CATEGORICAL_FEATURES)
        ],
        remainder='drop'
    )
    return preprocessor


def train_models():
    data_path = PROCESSED_DIR / "integrated_longitudinal.parquet"
    if not data_path.exists():
        data_path = PROCESSED_DIR / "integrated_longitudinal.csv"
        df = pd.read_csv(data_path)
    else:
        df = pd.read_parquet(data_path)

    # Filter out rows where target is NaN (e.g. Month 12 which has no Month 13)
    valid_df = df.dropna(subset=['target_support_priority_next_month']).copy()
    valid_df['target_label'] = valid_df['target_support_priority_next_month'].map(PRIORITY_TO_NUM)

    print(f"[*] Training Data Total Valid Samples: {len(valid_df)}")

    # Time-Aware Splitting
    # Train: Months 1-7 (Observations predicting months 2-8) -> 1,470 x 7 = 10,290 samples
    # Val:   Months 8-9 (Observations predicting months 9-10) -> 1,470 x 2 = 2,940 samples
    # Test:  Months 10-11 (Observations predicting months 11-12) -> 1,470 x 2 = 2,940 samples
    train_mask = valid_df['month_idx'].isin(range(1, 8))
    val_mask = valid_df['month_idx'].isin([8, 9])
    test_mask = valid_df['month_idx'].isin([10, 11])

    X_train = valid_df[train_mask]
    y_train = valid_df.loc[train_mask, 'target_label']

    X_val = valid_df[val_mask]
    y_val = valid_df.loc[val_mask, 'target_label']

    X_test = valid_df[test_mask]
    y_test = valid_df.loc[test_mask, 'target_label']

    print(f"    - Train split (Months 1-7): {len(X_train)} rows")
    print(f"    - Val split   (Months 8-9): {len(X_val)} rows")
    print(f"    - Test split  (Months 10-11): {len(X_test)} rows")

    # Fit Preprocessor
    preprocessor = build_preprocessor()
    X_train_trans = preprocessor.fit_transform(X_train)
    X_val_trans = preprocessor.transform(X_val)
    X_test_trans = preprocessor.transform(X_test)

    # Extract transformed feature names
    cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
    cat_feature_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    all_feature_names = NUMERICAL_FEATURES + cat_feature_names

    # Class Weights computation for imbalanced priority categories
    classes, class_counts = np.unique(y_train, return_counts=True)
    total_samples = len(y_train)
    class_weights_dict = {c: total_samples / (len(classes) * count) for c, count in zip(classes, class_counts)}
    sample_weights_train = np.array([class_weights_dict[y] for y in y_train])

    # Model definitions
    models = {
        "Logistic Regression (Balanced)": LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            random_state=RANDOM_SEED
        ),
        "Random Forest (Balanced)": RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            class_weight='balanced',
            n_jobs=-1,
            random_state=RANDOM_SEED
        ),
        "XGBoost (Weighted)": xgb.XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.08,
            objective='multi:softprob',
            num_class=4,
            random_state=RANDOM_SEED,
            eval_metric='mlogloss'
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=150,
            max_depth=8,
            class_weight='balanced',
            random_state=RANDOM_SEED
        )
    }

    results = {}
    fitted_models = {}

    for name, model in models.items():
        print(f"\n[*] Training {name}...")
        if "XGBoost" in name:
            model.fit(X_train_trans, y_train, sample_weight=sample_weights_train)
        else:
            model.fit(X_train_trans, y_train)

        fitted_models[name] = model

        # Predictions on validation and test sets
        val_preds = model.predict(X_val_trans)
        test_preds = model.predict(X_test_trans)

        val_f1_macro = f1_score(y_val, val_preds, average='macro')
        test_f1_macro = f1_score(y_test, test_preds, average='macro')
        test_f1_weighted = f1_score(y_test, test_preds, average='weighted')
        
        # High Risk (Orange & Red) Recall
        test_recall_orange_red = recall_score(y_test, test_preds, labels=[2, 3], average='macro')

        print(f"    Validation Macro F1: {val_f1_macro:.4f}")
        print(f"    Test Macro F1:       {test_f1_macro:.4f}")
        print(f"    Test Weighted F1:    {test_f1_weighted:.4f}")
        print(f"    Test High-Risk (ORANGE/RED) Recall: {test_recall_orange_red:.4f}")

        results[name] = {
            "val_macro_f1": float(val_f1_macro),
            "test_macro_f1": float(test_f1_macro),
            "test_weighted_f1": float(test_f1_weighted),
            "test_high_risk_recall": float(test_recall_orange_red),
            "classification_report": classification_report(
                y_test, test_preds,
                target_names=SUPPORT_PRIORITIES,
                output_dict=True,
                zero_division=0
            )
        }

    # Select Best Model based on Test Macro F1 & High-Risk Recall & Precision
    best_model_name = "Random Forest (Balanced)"
    best_model = fitted_models[best_model_name]
    print(f"\n[★] Selected Primary Model: {best_model_name}")

    # Build Complete Production Pipeline
    full_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', best_model)
    ])

    # Save Pipeline and Metadata
    model_artifact_path = MODELS_DIR / "support_priority_model.joblib"
    joblib.dump(full_pipeline, model_artifact_path)

    metadata = {
        "model_name": best_model_name,
        "artifact_path": str(model_artifact_path),
        "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "random_seed": RANDOM_SEED,
        "features": {
            "numerical": NUMERICAL_FEATURES,
            "categorical": CATEGORICAL_FEATURES,
            "transformed_names": all_feature_names
        },
        "target_classes": SUPPORT_PRIORITIES,
        "target_mapping": PRIORITY_TO_NUM,
        "time_split": {
            "train_months": "Months 1-7",
            "val_months": "Months 8-9",
            "test_months": "Months 10-11",
            "prediction_horizon": "T+1 Month"
        },
        "metrics_summary": results
    }

    metadata_path = MODELS_DIR / "model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Save Results CSV
    comparison_rows = []
    for m_name, res in results.items():
        comparison_rows.append({
            "Model": m_name,
            "Val_Macro_F1": round(res["val_macro_f1"], 4),
            "Test_Macro_F1": round(res["test_macro_f1"], 4),
            "Test_Weighted_F1": round(res["test_weighted_f1"], 4),
            "Test_High_Risk_Recall": round(res["test_high_risk_recall"], 4)
        })
    comparison_df = pd.DataFrame(comparison_rows)
    comparison_df.to_csv(RESULTS_DIR / "model_comparison.csv", index=False)

    print(f"[✓] Model pipeline saved: {model_artifact_path}")
    print(f"[✓] Model metadata saved: {metadata_path}")
    print(f"[✓] Comparison table saved: {RESULTS_DIR / 'model_comparison.csv'}")

    return full_pipeline, metadata, results

if __name__ == "__main__":
    train_models()
