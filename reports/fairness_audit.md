# SAATHI: Fairness & Subgroup Robustness Audit Report

## 1. Subgroup Empirical Evaluation on Test Split ($N = 2,940$)

We evaluated the primary High-Risk Detector across organizational and demographic subgroups to check for disparate false-positive or false-negative rates.

### A. Subgroup Breakdown by Department
| Department | Sample Size ($N$) | High-Risk Positives | Prevalence | Precision | Recall | F1-Score | False Positive Rate (FPR) | False Negative Rate (FNR) |
|---|---|---|---|---|---|---|---|---|
| **Human Resources** | 126 | 10 | 7.94% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |
| **Research & Development** | 1,922 | 192 | 9.99% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |
| **Sales** | 892 | 84 | 9.42% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |

### B. Subgroup Breakdown by Job Level
| Job Level | Sample Size ($N$) | High-Risk Positives | Prevalence | Precision | Recall | F1-Score | False Positive Rate (FPR) | False Negative Rate (FNR) |
|---|---|---|---|---|---|---|---|---|
| **Level 1** (Entry Level) | 1,086 | 106 | 9.76% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |
| **Level 2** (Junior Officers) | 1,068 | 92 | 8.61% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |
| **Level 3** (Mid-Level) | 436 | 52 | 11.93% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |
| **Level 4** (Senior Staff) | 212 | 24 | 11.32% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |
| **Level 5** (Executive Command) | 138 | 12 | 8.70% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |

### C. Subgroup Breakdown by Gender
| Gender | Sample Size ($N$) | High-Risk Positives | Prevalence | Precision | Recall | F1-Score | False Positive Rate (FPR) | False Negative Rate (FNR) |
|---|---|---|---|---|---|---|---|---|
| **Female** | 1,180 | 116 | 9.83% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |
| **Male** | 1,760 | 170 | 9.66% | **1.000** | **1.000** | **1.000** | **0.000** | **0.000** |

---

## 2. Ethical Safety & Real-World Validation Disclaimer

> ### ⚠️ CRITICAL SCIENTIFIC & ETHICAL DISCLAIMER:
> 1. **Synthetic Fairness Does NOT Guarantee Real-World Fairness**:
>    - The parity in precision ($1.00$) and recall ($1.00$) across departments and job levels is an artifact of the synthetic scenario engine, which distributed operational deployment scenarios uniformly across demographic attributes.
>    - In real-world operational forces, structural differences (e.g., specialized unit deployments, combat postings, geographic hardship allocations) may create demographic disparities in workload and recovery opportunities.
> 2. **No Disciplinary or Punitive Usage**:
>    - Predictions from SAATHI must never be used for promotion scoring, punitive disciplinary reviews, or performance appraisal.
>    - The system is designed strictly as a supportive occupational welfare decision-support tool.
> 3. **Future Real-World Validation Requirements**:
>    - Before deploying in production uniformed environments, rigorous fairness audits must be conducted across actual operational units, command regions, and battalion specializations under institutional review board (IRB) oversight.
