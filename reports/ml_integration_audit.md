# SAATHI — ML Integration & Inference Audit Report

**Smart India Hackathon (SIH) Problem Statement 26186**  
**Title:** AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**Organization:** Ministry of Home Affairs | CRPF, Police II Division  
**System:** SAATHI  
**Date:** September 2026  
**Status:** **AUDITED & VERIFIED (LOCKED ML ARTIFACTS CONFIRMED)**  

---

## 1. Locked ML Pipeline Verification

* **Artifacts Verified:**
  - `ml/models/support_priority_model.joblib`: Contains the trained `BalancedRandomForestClassifier` with Platt Calibration wrapper.
  - `ml/models/model_metadata.json`: Feature definitions, operational threshold ($\tau = 0.50$), calibration parameters, and evaluation summaries.
* **Inference Pipeline Path:**
  ```text
  Client Request (personnel_id)
        ↓
  PredictionService.get_latest_longitudinal_observation(personnel_id)
        ↓
  Personal Historical Baseline ($t \le T-1$ Causal History Window)
        ↓
  Feature Vector Construction (No target features, no future lookahead)
        ↓
  ML Adapter (`backend/app/ml/adapter.py`)
        ↓
  Random Forest Inference -> Platt Sigmoid Calibration ($P(\text{High Risk})$)
        ↓
  Welfare Support Priority Score ($S = 100 \times P$) & Priority Tier Mapping
        ↓
  Engineered Prediction Reliability Index ($R = f(\text{Certainty}, C, M)$)
        ↓
  SHAP Factor Attribution Decomposition
        ↓
  Deterministic Recommendation Engine
  ```

---

## 2. Personal Historical Baseline Integrity

* **Causal Window Guarantee:** Tested in `tests/test_baseline.py` and `backend/tests/test_analytics.py`. Baseline metrics for observation at time $T$ are strictly computed over $t \le T-1$.
* **Cold-Start Handling:** Personnel with $< 3$ months of history have `baseline_maturity_months < 3`. If core telemetry signals are missing, the **Data Completeness Gate** ($C < 0.35$) triggers `INSUFFICIENT_DATA` rather than outputting a false-negative zero score.

---

## 3. Score Semantics & Reliability Indicator Verification

* **Welfare Support Priority Score ($0.0 - 100.0$):**
  - Continuous calibrated indicator of high-risk operational welfare state.
  - Tiers: `GREEN` ($< 30.0$), `YELLOW` ($30.0 - 54.9$), `ORANGE` ($55.0 - 74.9$), `RED` ($\ge 75.0$).
  - **Verified:** All UI headers and labels explicitly use *"Welfare Support Priority Score"*. The forbidden terms (*"Depression"*, *"Mental illness"*, *"Stress diagnosis"*, *"Psychological failure"*) are completely excluded.
* **Prediction Reliability Indicator ($0\% - 100\%$):**
  - Engineered index combining model certainty, data completeness, and baseline history maturity.
  - **Verified:** Explicitly documented as an engineering reliability score, not a clinical confidence interval.

---

## 4. Explainability & Factor Attribution Consistency

* **Methodology:** Feature contributions are extracted from tree feature attributions and mapped to operational descriptions:
  - `duty_hours_pct_change_vs_baseline` -> *"Monthly Duty Hours vs Personal Baseline"*
  - `night_shifts_pct_change_vs_baseline` -> *"Night Shift Surge vs Personal Baseline"*
  - `days_since_prev_leave` -> *"Elapsed Duration Since Previous Leave"*
  - `workload_intensity_score` -> *"Total Monthly Workload Intensity"*
  - `rest_hours` -> *"Monthly Rest & Recovery Deficit"*
* **Verified:** Descriptions use non-clinical, operational language focusing on operational strain and recovery deficits.
