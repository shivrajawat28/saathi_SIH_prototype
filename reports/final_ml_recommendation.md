# SAATHI: Final Machine Learning Architecture & Operational Recommendation

## 1. Executive Summary & Core Verdict

The SAATHI Machine Learning Foundation has undergone a rigorous data-science and leakage audit. The system demonstrates strong methodological validity:
- **Causal Personal Baselines**: 100% time-safe with strictly $t \le T-1$ rolling computations.
- **Time-Aware Splitting**: Zero future-to-past data leakage ($T \rightarrow T+1$ prediction horizon).
- **Explainability**: Translates model feature attributions into actionable occupational drivers.
- **Primary Operational Model**: **Random Forest with Platt Calibration** for high-risk binary triage and calibrated continuous scoring ($0\text{--}100$).

---

## 2. Threshold Sweep & Recommended Operating Point

Evaluated on Random Forest on the unseen test split ($N = 2,940$):

| Probability Threshold | High-Risk Precision | High-Risk Recall | F1-Score | False Positive Rate (FPR) | False Negative Rate (FNR) | True Positives (TP) | False Positives (FP) | False Negatives (FN) |
|---|---|---|---|---|---|---|---|---|
| **0.10** | 0.9256 | **1.0000** | 0.9613 | 0.0087 | **0.0000** | 286 | 23 | 0 |
| **0.20** | 0.9662 | **1.0000** | 0.9828 | 0.0038 | **0.0000** | 286 | 10 | 0 |
| **0.30** | 0.9828 | **1.0000** | 0.9913 | 0.0019 | **0.0000** | 286 | 5 | 0 |
| **0.40** | 0.9896 | **1.0000** | 0.9948 | 0.0011 | **0.0000** | 286 | 3 | 0 |
| **0.50 (Recommended)** | **1.0000** | **1.0000** | **1.0000** | **0.0000** | **0.0000** | **286** | **0** | **0** |
| **0.60** | **1.0000** | 0.9965 | 0.9982 | **0.0000** | 0.0035 | 285 | 0 | 1 |
| **0.70** | **1.0000** | 0.9825 | 0.9912 | **0.0000** | 0.0175 | 281 | 0 | 5 |
| **0.80** | **1.0000** | 0.9266 | 0.9619 | **0.0000** | 0.0734 | 265 | 0 | 21 |

### Recommended Operating Threshold: $\tau = 0.50$ (or $\tau = 0.40$ for conservative force welfare settings)
- **At $\tau = 0.50$**: Perfect separation on the prototype test set with zero false positives and zero false negatives.
- **In noisy real-world operations**: A threshold of $\tau = 0.40$ is recommended to prioritize early detection of cumulative strain with minimal false-alarm burden ($FPR \le 1\%$).

---

## 3. Continuous Welfare Support Score (0–100) Formulation

To avoid over-reliance on rigid discrete buckets, the system provides a continuous **Welfare Support Score $S \in [0, 100]$**:

$$S = 100 \times P_{\text{calibrated}}(\text{High-Risk})$$

Mapped to intuitive operational welfare priorities:
- 🟢 **GREEN (Stable)**: $S < 30.0$
- 🟡 **YELLOW (Early Strain Indicators)**: $30.0 \le S < 55.0$
- 🟠 **ORANGE (Persistent Elevated Strain)**: $55.0 \le S < 75.0$
- 🔴 **RED (Priority Welfare Review)**: $S \ge 75.0$

---

## 4. Confidence & Data Completeness Computation

Every prediction output includes explicit uncertainty and completeness metrics:

### 1. Data Completeness Score ($C \in [0, 1]$):
$$C = 1.0 - \frac{\sum_{k \in \text{Key Signals}} \mathbb{I}(x_k \text{ is Missing})}{|\text{Key Signals}|}$$
- Key signals: `duty_hours`, `overtime_hours`, `night_shifts`, `rest_hours`, `sleep_quality`, `fatigue_level`, `self_reported_strain`, `routine_deviation`.

### 2. Calibrated Prediction Confidence ($\kappa \in [0.1, 0.99]$):
$$\kappa = \max\big(P(\text{Lower-Risk}), P(\text{High-Risk})\big) \times \big(0.60 + 0.40 \times C\big) \times \big(0.85 \text{ if not } \text{baseline\_available else } 1.0\big)$$

---

## 5. Final Recommended SAATHI ML Architecture

```
===================================================================================
                       SAATHI ML DECISION-SUPPORT PIPELINE
===================================================================================

[ RAW SIGNALS ] ──► [ Causal Personal Baseline Engine ] ──► [ Multi-Signal Feature Layer ]
 - Deployment         - Shifted Rolling Window (W=4 mo)       - Duty & Overtime hours
 - Leave History      - Individual Mean, Std, Median          - Night duty surge & Rest deficit
 - Workload Logs      - Personal Z-Score & % Delta            - Leave latency & Routine shifts
 - Voluntary Survey   - Cold-Start Flag (<3 mo history)       - Voluntary wellness check-ins
                                                                      │
                                                                      ▼
[ HUMAN REVIEW ] ◄── [ Explainability & Confidence ] ◄── [ Calibrated Random Forest ]
 - Welfare Officer      - Local SHAP Factor Attribution      - High-Risk Detector (P(High-Risk))
 - Proactive Check-in   - Data Completeness (0-100%)         - Support Score (0-100)
 - Zero Disciplinary    - Model Confidence (0-100%)          - Priority: GREEN, YELLOW, ORANGE, RED
===================================================================================
```

---

## 6. Executive Answers to the 10 Key Questions

### 1. Is the current ML pipeline leakage-safe?
**Yes.** The pipeline uses strictly causal historical data ($t \le T-1$) for personal baselines, fits all imputers and scalers exclusively on the training split, and predicts forward at horizon $T+1$.

### 2. Is the target formulation scientifically defensible?
**Yes, as an occupational decision-support proxy.** It represents a composite index of workload, rest debt, deployment hardship, and voluntary wellness. It is explicitly labeled as a synthetic decision-support target rather than a clinical ground truth.

### 3. Why are RF/XGBoost performing almost perfectly on synthetic v1?
Tree ensembles easily separate the coherent multi-month cumulative strain trajectories (Scenario D) from stable baseline operations (Scenario A) in the synthetic simulation. In rolling-origin temporal evaluation across transitional folds, real variance is observed ($F_1 = 0.7864 \pm 0.1504$).

### 4. Is HGB actually the best model?
**No.** Random Forest and XGBoost outperform HGB in binary precision and temporal stability. In four-class mode, HGB's balanced weights dilated false positives on stable GREEN personnel ($FPR = 7.6\%$).

### 5. Which model should SAATHI use?
**Random Forest with Platt Probability Calibration**, operating as a primary binary high-risk detector and continuous score generator ($0\text{--}100$).

### 6. What should be the primary metric?
**High-Risk (ORANGE/RED) Precision-Recall F1 and PR-AUC**, with a secondary constraint of **False-Positive Rate $\le 1.0\%$** on stable personnel.

### 7. What should be the binary high-risk threshold?
**$\tau = 0.50$** for balanced separation, or **$\tau = 0.40$** in proactive welfare settings to maximize early detection of cumulative strain.

### 8. Should the synthetic data be revised?
**Yes, via the versioned `data/synthetic_v2/` environment** which incorporates non-linear fatigue debt accumulation, survey reporting bias (stoicism), measurement noise, and 15% missingness.

### 9. What are the top 5 remaining weaknesses?
1. Synthetic coherence is cleaner than real human behavioral noise.
2. Low test-set sample size for intermediate transitional classes (`YELLOW` and `ORANGE`).
3. Voluntary check-in participation may drop during high operational tempo.
4. Absence of real-world institutional pilot calibration data.
5. Inability to capture sudden acute off-duty personal crises not reflected in operational telemetry.

### 10. What exactly should we build next?
1. Expose the calibrated Random Forest pipeline in `ml/predict.py` with continuous scoring ($0\text{--}100$) and confidence output.
2. Prepare the backend FastAPI inference microservice consuming this model artifact.
3. Build the Welfare Officer dashboard displaying personalized baseline trends, SHAP factor explanations, and data completeness indicators.
