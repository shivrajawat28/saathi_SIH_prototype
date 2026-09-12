# SAATHI ML Pipeline Audit & Architecture Specification

## 1. Executive Summary & Information Flow

The SAATHI machine learning pipeline is designed as an **occupational decision-support system** for authorized welfare officers to identify cumulative strain and prioritize supportive welfare reviews. It strictly excludes medical/clinical diagnosis and invasive surveillance.

### End-to-End Pipeline Architecture Diagram

```
+-------------------------------------------------------------------------------+
| 1. RAW DATA SOURCES                                                           |
|    - Official HR Benchmark (data/official_hr/HR_Analytics.csv) [READ-ONLY]   |
|    - Privacy-Preserving Synthetic Scenarios (data/synthetic/ or synthetic_v2/)|
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| 2. PSEUDONYMIZED MASTER GENERATION (data/processed/personnel_master.csv)       |
|    - 1,470 Deduplicated Personnel IDs: P-000001 to P-001470                   |
|    - Normalization of static organizational attributes & baseline satisfaction|
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| 3. LONGITUDINAL INTEGRATION & CAUSAL FEATURE ENGINEERING                       |
|    - 12 Monthly observation snapshots across 5 domains                        |
|    - Deployment + Leave + Workload + Voluntary Wellness + Behavioral Changes  |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| 4. PERSONAL BASELINE ENGINE (ml/baseline/personal_baseline.py)                |
|    - Strictly Causal Rolling Window (W=4 months, shifted by 1 period)         |
|    - Mean, Std, Median, Delta, % Change, Personal Z-Scores, Trend Lags        |
|    - Cold-Start Fallback (<3 months) with baseline_available = False          |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| 5. NON-LEAKING FORWARD TARGET FORMULATION (Horizon T+1)                        |
|    - Observation Month T features predict Welfare Priority at Month T+1       |
|    - Discrete: GREEN (<35), YELLOW (35-55), ORANGE (55-75), RED (>=75)        |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| 6. STRICT TIME-AWARE SPLITTING                                                |
|    - Train Split: Months 1 to 7 (10,290 samples)                              |
|    - Validation Split: Months 8 to 9 (2,940 samples)                          |
|    - Test Split: Months 10 to 11 (2,940 samples)                              |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| 7. MODEL TRAINING, THRESHOLD TUNING & CALIBRATION                              |
|    - Primary Detector: Calibrated Random Forest / HistGradientBoosting        |
|    - Binary High-Risk (ORANGE/RED) + Multi-Class Secondary Categorization     |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
| 8. INFERENCE & EXPLAINABILITY SERVICE (ml/predict.py)                         |
|    - Output: Priority + Continuous Score (0-100) + Confidence + Completeness  |
|    - Local SHAP Factor Attribution (Direction + Quantitative Impact)          |
|    - Automatic Incomplete Data Fallback (<35% completeness)                   |
+-------------------------------------------------------------------------------+
```

---

## 2. Pipeline Component Audit

### Component 1: Data Ingestion & Master Generation
- **Source**: `HR_Analytics.csv` is parsed safely in read-only mode (MD5: `4bbc84d521f2e9e46bcb37d88c2c2d7b`).
- **Deduplication**: 1,480 raw rows contain 10 duplicate entries (from benchmark appending), cleanly resolved into **1,470 unique personnel**.
- **Pseudonymization**: IDs mapped to `P-000001` through `P-001470`.
- **Ethical Boundary**: `Attrition` is segregated as an organizational metric and never used as a stress/burnout label.

### Component 2: Synthetic Longitudinal Generation
- Simulates 12 monthly periods per personnel across 6 realistic occupational scenarios:
  1. *Stable Operation* (50%)
  2. *High Tempo* (15%)
  3. *Extended Deployment* (12%)
  4. *Cumulative Strain* (10%)
  5. *Recovery & Rebound* (8%)
  6. *Resilient Noise / False-Alarm Resistance* (5%)

### Component 3: Personal Baseline Engine
- Calculates individual historical norms using strictly $t \le T-1$.
- Computes percentage change $\Delta\%$ and personal z-score $z = \frac{x_T - \mu_{T-1}}{\sigma_{T-1}}$.
- Flag `baseline_available` is set to `False` for $T < 3$, penalizing cold-start confidence.

### Component 4: Preprocessing & ColumnTransformer
- **Numerical Pipeline**: Median Imputation $\rightarrow$ Standard Scaling.
- **Categorical Pipeline**: Constant Missing Imputation $\rightarrow$ One-Hot Encoding with `handle_unknown='ignore'`.
- Fitted strictly on the **Training Split (Months 1–7)** to guarantee zero preprocessing leakage.

### Component 5: Time-Aware Evaluation
- Split strictly on the time axis:
  - Training: `2025-01-01` to `2025-07-01`
  - Validation: `2025-08-01` to `2025-09-01`
  - Test: `2025-10-01` to `2025-11-01`
- Temporal boundary prevents future information leakage into model training.
