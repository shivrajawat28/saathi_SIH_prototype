"""
SAATHI: Model Evaluation & Fairness Audit Module
Generates comprehensive performance metrics, confusion matrices, high-risk trade-off analysis,
and subgroup fairness checks across organizational categories.
Outputs ml/results/evaluation_report.json and ml/results/confusion_matrix.png.
"""

import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    f1_score,
    precision_score,
    recall_score
)

from ml.config import (
    PROCESSED_DIR,
    MODELS_DIR,
    RESULTS_DIR,
    SUPPORT_PRIORITIES,
    PRIORITY_TO_NUM,
    NUM_TO_PRIORITY
)

def evaluate_pipeline():
    # 1. Load pipeline and metadata
    model_path = MODELS_DIR / "support_priority_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Model pipeline not found at {model_path}. Train model first.")

    pipeline = joblib.load(model_path)
    
    with open(MODELS_DIR / "model_metadata.json", "r") as f:
        metadata = json.load(f)

    # 2. Load test split
    data_path = PROCESSED_DIR / "integrated_longitudinal.parquet"
    if not data_path.exists():
        data_path = PROCESSED_DIR / "integrated_longitudinal.csv"
        df = pd.read_csv(data_path)
    else:
        df = pd.read_parquet(data_path)

    test_df = df[df['month_idx'].isin([10, 11])].dropna(subset=['target_support_priority_next_month']).copy()
    y_true = test_df['target_support_priority_next_month'].map(PRIORITY_TO_NUM).values
    
    # 3. Model Predictions & Probabilities
    y_pred = pipeline.predict(test_df)
    y_proba = pipeline.predict_proba(test_df)

    # 4. Metrics calculation
    macro_f1 = float(f1_score(y_true, y_pred, average='macro'))
    weighted_f1 = float(f1_score(y_true, y_pred, average='weighted'))
    macro_recall = float(recall_score(y_true, y_pred, average='macro'))
    macro_precision = float(precision_score(y_true, y_pred, average='macro', zero_division=0))

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3])

    # Per-class performance
    class_report = classification_report(
        y_true, y_pred,
        target_names=SUPPORT_PRIORITIES,
        output_dict=True,
        zero_division=0
    )

    # 5. Plot Confusion Matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=SUPPORT_PRIORITIES,
        yticklabels=SUPPORT_PRIORITIES
    )
    plt.title(f"SAATHI Support Priority Confusion Matrix (Test Split: Months 11-12)\nModel: {metadata['model_name']}", fontsize=12)
    plt.xlabel("Predicted Support Priority", fontsize=11)
    plt.ylabel("Ground Truth Latent Priority", fontsize=11)
    plt.tight_layout()
    cm_plot_path = RESULTS_DIR / "confusion_matrix.png"
    plt.savefig(cm_plot_path, dpi=300)
    plt.close()

    # 6. High-Risk (ORANGE/RED) Trade-Off Analysis
    # Orange and Red classes are indices 2 and 3
    is_high_risk_true = np.isin(y_true, [2, 3])
    is_high_risk_pred = np.isin(y_pred, [2, 3])

    high_risk_tp = int(np.logical_and(is_high_risk_true, is_high_risk_pred).sum())
    high_risk_fp = int(np.logical_and(~is_high_risk_true, is_high_risk_pred).sum())
    high_risk_fn = int(np.logical_and(is_high_risk_true, ~is_high_risk_pred).sum())
    high_risk_tn = int(np.logical_and(~is_high_risk_true, ~is_high_risk_pred).sum())

    high_risk_recall = float(high_risk_tp / max((high_risk_tp + high_risk_fn), 1))
    high_risk_precision = float(high_risk_tp / max((high_risk_tp + high_risk_fp), 1))

    # 7. Subgroup Fairness & Disparity Audit
    test_df['y_true'] = y_true
    test_df['y_pred'] = y_pred

    subgroup_analysis = {}
    for group_col in ['department', 'job_role', 'job_level']:
        if group_col in test_df.columns:
            group_metrics = {}
            for val, group in test_df.groupby(group_col):
                if len(group) >= 20: # Minimum sample threshold
                    g_true = group['y_true'].values
                    g_pred = group['y_pred'].values
                    group_metrics[str(val)] = {
                        "sample_size": len(group),
                        "macro_f1": round(float(f1_score(g_true, g_pred, average='macro', zero_division=0)), 4),
                        "accuracy": round(float(np.mean(g_true == g_pred)), 4),
                        "high_risk_recall": round(float(np.mean(g_pred[np.isin(g_true, [2, 3])] == g_true[np.isin(g_true, [2, 3])])) if np.sum(np.isin(g_true, [2, 3])) > 0 else 1.0, 4)
                    }
            subgroup_analysis[group_col] = group_metrics

    # 8. Compile Comprehensive Evaluation Report
    evaluation_report = {
        "model_name": metadata["model_name"],
        "evaluation_date": metadata["training_date"],
        "test_samples_count": len(test_df),
        "overall_metrics": {
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "macro_precision": round(macro_precision, 4),
            "macro_recall": round(macro_recall, 4),
            "high_risk_priority_recall": round(high_risk_recall, 4),
            "high_risk_priority_precision": round(high_risk_precision, 4)
        },
        "confusion_matrix": cm.tolist(),
        "per_class_metrics": class_report,
        "high_risk_tradeoff_analysis": {
            "true_positives": high_risk_tp,
            "false_positives": high_risk_fp,
            "false_negatives": high_risk_fn,
            "true_negatives": high_risk_tn,
            "interpretation": "A false positive triggers a supportive, non-punitive welfare review. A false negative risks delayed support for personnel in elevated strain. The model prioritizes high recall on elevated tiers."
        },
        "fairness_and_subgroup_audit": subgroup_analysis,
        "ethical_disclaimer": "SAATHI is a decision-support system for authorized welfare officers. Outputs reflect operational and voluntary wellness patterns, not clinical diagnoses or disciplinary assessments."
    }

    report_path = RESULTS_DIR / "evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(evaluation_report, f, indent=2)

    print(f"[✓] Evaluation report written to: {report_path}")
    print(f"[✓] Confusion matrix saved to:   {cm_plot_path}")
    print(f"    - Macro F1:                {macro_f1:.4f}")
    print(f"    - High Risk (ORANGE/RED) Recall: {high_risk_recall:.4f}")
    print(f"    - High Risk Precision:     {high_risk_precision:.4f}")

    return evaluation_report

if __name__ == "__main__":
    evaluate_pipeline()
