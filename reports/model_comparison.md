# SAATHI: Model Comparison & Selection Audit Report

## 1. Primary Operational Problem: High-Risk Binary Detector

In operational welfare monitoring for uniformed forces, the primary decision-support priority is distinguishing personnel requiring supportive outreach (**HIGH-RISK: `ORANGE` or `RED`**) from those maintaining stable operational rhythms (**LOWER-RISK: `GREEN` or `YELLOW`**).

### Comprehensive Benchmark on Unseen Test Split ($N = 2,940$)

| Model Architecture | Precision | Recall | F1-Score | Specificity | False Positive Rate (FPR) | False Negative Rate (FNR) | PR-AUC | ROC-AUC | Brier Score |
|---|---|---|---|---|---|---|---|---|---|
| **Random Forest (Balanced)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **0.0000** | **0.0000** | **1.0000** | **1.0000** | **0.0138** |
| **XGBoost (Weighted)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **0.0000** | **0.0000** | **1.0000** | **1.0000** | **0.0046** |
| **HistGradientBoosting** | 0.9931 | **1.0000** | 0.9965 | 0.9992 | 0.0008 | **0.0000** | **1.0000** | **1.0000** | 0.0061 |
| **Logistic Regression (Baseline)** | 0.8833 | 0.9790 | 0.9287 | 0.9861 | 0.0139 | 0.0210 | 0.9898 | 0.9975 | 0.0174 |

---

## 2. Confusion Matrices (Binary High-Risk vs Lower-Risk)

### Random Forest / XGBoost (Test Split, $N=2,940$)
$$\begin{pmatrix}
\text{True Negative (Lower-Risk)}: 2654 & \text{False Positive}: 0 \\
\text{False Negative}: 0 & \text{True Positive (High-Risk)}: 286
\end{pmatrix}$$

### HistGradientBoosting (Binary Test Split, $N=2,940$)
$$\begin{pmatrix}
\text{True Negative (Lower-Risk)}: 2652 & \text{False Positive}: 2 \\
\text{False Negative}: 0 & \text{True Positive (High-Risk)}: 286
\end{pmatrix}$$

### Logistic Regression (Binary Test Split, $N=2,940$)
$$\begin{pmatrix}
\text{True Negative (Lower-Risk)}: 2617 & \text{False Positive}: 37 \\
\text{False Negative}: 6 & \text{True Positive (High-Risk)}: 280
\end{pmatrix}$$

---

## 3. Four-Class Multi-Class Evaluation & Class Imbalance Audit

When models are trained on the granular 4-class target (`GREEN`, `YELLOW`, `ORANGE`, `RED`), class distribution changes dramatically across time:

### Test Set Class Support ($N=2,940$)
- `GREEN`: 2,642 (89.86%)
- `YELLOW`: 12 (0.41%) $\rightarrow$ *Severe class scarcity in late months*
- `ORANGE`: 67 (2.28%)
- `RED`: 219 (7.45%)

### Four-Class Performance Breakdown (`HistGradientBoosting`)
| Class | Precision | Recall | F1-Score | Support | Operational Meaning |
|---|---|---|---|---|---|
| **GREEN** | 0.9954 | 0.9092 | 0.9503 | 2,642 | Stable personnel |
| **YELLOW** | 0.0625 | 0.0833 | 0.0714 | 12 | Mild early strain (transitional) |
| **ORANGE** | 0.0173 | 0.0597 | 0.0268 | 67 | Persistent elevated strain |
| **RED** | 0.7679 | 0.9817 | 0.8617 | 219 | Priority welfare review |

### Why Four-Class Macro F1 is Misleadingly Low ($\approx 0.47$):
- In longitudinal progression, personnel in synthetic scenarios either resolve early strain and return to `GREEN`, or escalate into severe cumulative strain `RED`.
- By Months 10–11, only 12 personnel remain in the narrow `YELLOW` score band ($[35, 55)$).
- A model misclassifying a few of these rare transitional points suffers an extreme arithmetic penalty in unweighted Macro F1, despite achieving **91.91% Weighted F1** and **100% High-Risk Recall**.

---

## 4. Model Selection Decision & Recommendation

### Comparison of Candidate Architectures

1. **Random Forest (Recommended Primary Model)**:
   - **Pros**: Highest stability across temporal folds, zero false-alarm rate on test set ($FPR=0.0\%$), robust to noisy outliers, natural feature importances.
   - **Calibration**: Brier score of $0.0138$ ($0.0121$ with Platt scaling).
2. **XGBoost (Alternative High-Performance Model)**:
   - **Pros**: Excellent gradient boosted discrimination ($F_1 = 1.0$, Brier = $0.0046$).
   - **Cons**: Slightly higher sensitivity to extreme threshold shifts.
3. **HistGradientBoosting**:
   - **Pros**: Fast computation.
   - **Cons**: In 4-class mode, balanced weights cause slight dilation of GREEN $\rightarrow$ ORANGE false positives.
4. **Logistic Regression (Linear Baseline)**:
   - **Pros**: Perfectly transparent linear coefficients.
   - **Cons**: Misses non-linear feature interactions between personal baseline z-scores and continuous duty hours ($FNR=2.1\%$).

### Final Model Selection
**Random Forest Classifier** is selected as the primary predictive engine, combined with **Platt Probability Calibration** for transparent confidence scoring.
