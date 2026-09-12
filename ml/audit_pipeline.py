"""
SAATHI: Rigorous ML Validation & Leakage Audit Script
Computes all audit metrics, distributions, calibration, correlations, subgroup disparities,
and generates empirical evidence for the audit report.
"""

import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
    brier_score_loss
)
from sklearn.calibration import calibration_curve

from ml.config import (
    PROCESSED_DIR,
    MODELS_DIR,
    RESULTS_DIR,
    SUPPORT_PRIORITIES,
    PRIORITY_TO_NUM,
    NUM_TO_PRIORITY,
    RANDOM_SEED
)
from ml.train import build_preprocessor, NUMERICAL_FEATURES, CATEGORICAL_FEATURES
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
import xgboost as xgb

def run_audit():
    # Load integrated dataset
    data_path = PROCESSED_DIR / "integrated_longitudinal.parquet"
    if not data_path.exists():
        data_path = PROCESSED_DIR / "integrated_longitudinal.csv"
        df = pd.read_csv(data_path)
    else:
        df = pd.read_parquet(data_path)

    valid_df = df.dropna(subset=['target_support_priority_next_month']).copy()
    valid_df['target_label'] = valid_df['target_support_priority_next_month'].map(PRIORITY_TO_NUM)

    train_df = valid_df[valid_df['month_idx'].isin(range(1, 8))].copy()
    val_df = valid_df[valid_df['month_idx'].isin([8, 9])].copy()
    test_df = valid_df[valid_df['month_idx'].isin([10, 11])].copy()

    # 1. CLASS DISTRIBUTION AUDIT
    print("==================================================")
    print("1. CLASS DISTRIBUTION AUDIT")
    print("==================================================")
    splits = {"TRAIN (Months 1-7)": train_df, "VAL (Months 8-9)": val_df, "TEST (Months 10-11)": test_df}
    dist_summary = {}
    for s_name, s_df in splits.items():
        total = len(s_df)
        counts = s_df['target_support_priority_next_month'].value_counts()
        print(f"\n--- {s_name} (Total: {total}) ---")
        dist_summary[s_name] = {}
        for c in SUPPORT_PRIORITIES:
            cnt = int(counts.get(c, 0))
            pct = (cnt / total) * 100
            dist_summary[s_name][c] = {"count": cnt, "pct": round(pct, 2)}
            print(f"  {c:7s}: {cnt:5d} ({pct:6.2f}%)")

    # 2. MODELS TRAINING & MULTI-MODEL COMPARISON
    print("\n==================================================")
    print("2. RE-EVALUATING ALL 4 MODELS ON UNSEEN TEST SPLIT")
    print("==================================================")
    preprocessor = build_preprocessor()
    X_train_trans = preprocessor.fit_transform(train_df)
    X_val_trans = preprocessor.transform(val_df)
    X_test_trans = preprocessor.transform(test_df)

    y_train = train_df['target_label'].values
    y_val = val_df['target_label'].values
    y_test = test_df['target_label'].values

    # Class weights for training
    classes, class_counts = np.unique(y_train, return_counts=True)
    total_samples = len(y_train)
    class_weights_dict = {c: total_samples / (len(classes) * count) for c, count in zip(classes, class_counts)}
    sample_weights_train = np.array([class_weights_dict[y] for y in y_train])

    models = {
        "Logistic Regression": LogisticRegression(class_weight='balanced', max_iter=1000, random_state=RANDOM_SEED),
        "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=12, class_weight='balanced', n_jobs=-1, random_state=RANDOM_SEED),
        "XGBoost": xgb.XGBClassifier(n_estimators=150, max_depth=5, learning_rate=0.08, objective='multi:softprob', num_class=4, random_state=RANDOM_SEED, eval_metric='mlogloss'),
        "HistGradientBoosting": HistGradientBoostingClassifier(max_iter=150, max_depth=8, class_weight='balanced', random_state=RANDOM_SEED)
    }

    model_results = {}
    predictions_dict = {}
    probas_dict = {}

    for name, model in models.items():
        if "XGBoost" in name:
            model.fit(X_train_trans, y_train, sample_weight=sample_weights_train)
        else:
            model.fit(X_train_trans, y_train)

        test_pred = model.predict(X_test_trans)
        predictions_dict[name] = test_pred
        if hasattr(model, "predict_proba"):
            probas_dict[name] = model.predict_proba(X_test_trans)

        # High-risk binary mapping (Orange=2 or Red=3 vs Green=0 or Yellow=1)
        y_test_hr = np.isin(y_test, [2, 3]).astype(int)
        pred_hr = np.isin(test_pred, [2, 3]).astype(int)

        macro_f1 = f1_score(y_test, test_pred, average='macro')
        weighted_f1 = f1_score(y_test, test_pred, average='weighted')
        acc = accuracy_score(y_test, test_pred)
        hr_p = precision_score(y_test_hr, pred_hr, zero_division=0)
        hr_r = recall_score(y_test_hr, pred_hr, zero_division=0)
        hr_f1 = f1_score(y_test_hr, pred_hr, zero_division=0)

        model_results[name] = {
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "accuracy": round(acc, 4),
            "hr_precision": round(hr_p, 4),
            "hr_recall": round(hr_r, 4),
            "hr_f1": round(hr_f1, 4),
            "report": classification_report(y_test, test_pred, target_names=SUPPORT_PRIORITIES, output_dict=True, zero_division=0),
            "cm": confusion_matrix(y_test, test_pred, labels=[0, 1, 2, 3]).tolist()
        }

    # 3. CONFUSION MATRIX & HIGH-RISK DEEP DIVE FOR BEST MODEL
    hgb_res = model_results["HistGradientBoosting"]
    hgb_cm = np.array(hgb_res["cm"])
    print("\n--- HistGradientBoosting Confusion Matrix (Rows: True, Cols: Pred) ---")
    print("Labels: [GREEN, YELLOW, ORANGE, RED]")
    print(hgb_cm)

    # 4. TARGET CONSTRUCTION & FEATURE LEAKAGE AUDIT
    print("\n==================================================")
    print("4. TARGET CONSTRUCTION & LEAKAGE CHECK")
    print("==================================================")
    # Check if target variables or future variables are present in the feature list
    used_features = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    print(f"Total features used by model: {len(used_features)}")
    
    suspicious_features = [f for f in used_features if any(term in f.lower() for term in ['target', 'next_month', 'latent_strain', 'period_support'])]
    print(f"Suspicious Target Leakage Features in Model Feature List: {suspicious_features}")

    # 5. PERSONAL BASELINE ROLLING LEAKAGE CHECK
    print("\n==================================================")
    print("5. PERSONAL BASELINE LEAKAGE PROOF")
    print("==================================================")
    # Verify for a single person that baseline values at month T only reflect <= T-1
    sample_p = df[df['personnel_id'] == 'P-000001'].sort_values('month_idx')
    print("Sample Personnel P-000001 Monthly Duty Hours vs Rolling Mean:")
    for _, row in sample_p[['month_idx', 'duty_hours', 'duty_hours_personal_mean', 'duty_hours_pct_change_vs_baseline']].iterrows():
        print(f"  Month {int(row['month_idx']):2d}: Duty={row['duty_hours']:.1f}, BaselineMean={row['duty_hours_personal_mean']:.1f}, PctChange={row['duty_hours_pct_change_vs_baseline']:+.1f}%")

    # 6. TEMPORAL DATES AUDIT
    print("\n==================================================")
    print("6. TEMPORAL SPLIT DATES")
    print("==================================================")
    print(f"TRAIN: Months {train_df['month_idx'].min()} to {train_df['month_idx'].max()} | Dates: {train_df['date'].min()} to {train_df['date'].max()} | Target Months: 2 to 8")
    print(f"VAL:   Months {val_df['month_idx'].min()} to {val_df['month_idx'].max()} | Dates: {val_df['date'].min()} to {val_df['date'].max()} | Target Months: 9 to 10")
    print(f"TEST:  Months {test_df['month_idx'].min()} to {test_df['month_idx'].max()} | Dates: {test_df['date'].min()} to {test_df['date'].max()} | Target Months: 11 to 12")

    # 7. CORRELATION & DETERMINISM ANALYSIS
    print("\n==================================================")
    print("7. SYNTHETIC CORRELATIONS & NOISE")
    print("==================================================")
    corr_cols = [
        'duty_hours', 'overtime_hours', 'night_shifts', 'rest_hours',
        'workload_score', 'sleep_quality', 'fatigue_level', 'self_reported_strain',
        'routine_deviation', 'target_support_score_next_month'
    ]
    corr_matrix = df[corr_cols].corr()
    print("Correlation with target_support_score_next_month:")
    print(corr_matrix['target_support_score_next_month'].sort_values(ascending=False))

    # Check Scenario F (Resilient Noise) stats
    print("\nScenario F (Resilient Noise) Representation:")
    # Filter by personnel who had high workload but low strain
    scen_f_samples = df[(df['workload_score'] > 60) & (df['self_reported_strain'] <= 2.5)]
    print(f"Total observations with High Workload (>60) but Low Strain (<=2.5): {len(scen_f_samples)}")
    print(f"Target distribution for these resilient cases:")
    print(scen_f_samples['target_support_priority_next_month'].value_counts())

    # 8. SUBGROUP FAIRNESS AUDIT ON TEST SET
    print("\n==================================================")
    print("8. SUBGROUP FAIRNESS AUDIT (TEST SET)")
    print("==================================================")
    hgb_pred = predictions_dict["HistGradientBoosting"]
    test_df['pred_label'] = hgb_pred
    test_df['y_true_hr'] = np.isin(y_test, [2, 3]).astype(int)
    test_df['y_pred_hr'] = np.isin(hgb_pred, [2, 3]).astype(int)

    fairness_results = {}
    for group_col in ['department', 'job_role', 'job_level']:
        print(f"\n--- Subgroup: {group_col} ---")
        fairness_results[group_col] = {}
        for val, grp in test_df.groupby(group_col):
            if len(grp) >= 15:
                gt = grp['y_true_hr'].values
                pr = grp['y_pred_hr'].values
                
                tp = int(np.sum((gt == 1) & (pr == 1)))
                fp = int(np.sum((gt == 0) & (pr == 1)))
                fn = int(np.sum((gt == 1) & (pr == 0)))
                tn = int(np.sum((gt == 0) & (pr == 0)))

                rec = tp / max(tp + fn, 1)
                prec = tp / max(tp + fp, 1)
                f1 = 2 * prec * rec / max(prec + rec, 1e-6)
                fpr = fp / max(fp + tn, 1)
                fnr = fn / max(fn + tp, 1)

                fairness_results[group_col][str(val)] = {
                    "sample_size": len(grp),
                    "positives": int(np.sum(gt == 1)),
                    "precision": round(prec, 4),
                    "recall": round(rec, 4),
                    "f1": round(f1, 4),
                    "fpr": round(fpr, 4),
                    "fnr": round(fnr, 4)
                }
                print(f"  {str(val):25s} | N={len(grp):4d} (Pos={np.sum(gt==1):3d}) | Prec={prec:.3f}, Rec={rec:.3f}, F1={f1:.3f}, FPR={fpr:.3f}, FNR={fnr:.3f}")

    # 9. CALIBRATION & BRIER SCORE
    print("\n==================================================")
    print("9. CALIBRATION & BRIER SCORE AUDIT")
    print("==================================================")
    hgb_probas = probas_dict["HistGradientBoosting"]
    # Binary high risk probability = P(Orange) + P(Red)
    p_high_risk = hgb_probas[:, 2] + hgb_probas[:, 3]
    brier_hr = brier_score_loss(test_df['y_true_hr'], p_high_risk)
    print(f"High-Risk Binary Brier Score: {brier_hr:.4f} (Lower is better, <0.25 indicates better than chance)")

    # Plot Calibration Curve
    prob_true, prob_pred = calibration_curve(test_df['y_true_hr'], p_high_risk, n_bins=10, strategy='uniform')
    plt.figure(figsize=(7, 5))
    plt.plot(prob_pred, prob_true, marker='o', linewidth=2, label='HistGradientBoosting')
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfect Calibration')
    plt.title('High-Risk (ORANGE/RED) Calibration Curve', fontsize=12)
    plt.xlabel('Mean Predicted Probability', fontsize=11)
    plt.ylabel('Observed True Proportion', fontsize=11)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    calib_plot_path = RESULTS_DIR / "calibration_curve.png"
    plt.savefig(calib_plot_path, dpi=300)
    plt.close()
    print(f"Calibration plot saved to: {calib_plot_path}")

    # Save full audit results to JSON
    audit_data = {
        "class_distributions": dist_summary,
        "model_comparison": model_results,
        "fairness_audit": fairness_results,
        "brier_score_high_risk": round(brier_hr, 4),
        "calibration_curve": {
            "predicted_prob": prob_pred.tolist(),
            "true_prob": prob_true.tolist()
        }
    }
    with open(RESULTS_DIR / "audit_metrics.json", "w") as f:
        json.dump(audit_data, f, indent=2)

    print(f"\n[✓] Audit metrics successfully computed and saved to {RESULTS_DIR / 'audit_metrics.json'}")

if __name__ == "__main__":
    run_audit()
