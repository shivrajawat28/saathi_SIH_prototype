# SAATHI Data Manifest & Provenance Specification

## 1. Provenance Classification Summary

| Dataset Path | Source Classification | Type | Record Count | Time Horizon | Provenance / Generator |
|---|---|---|---|---|---|
| `data/official_hr/HR_Analytics.csv` | **External Anonymized HR Dataset** | Tabular HR Master (Read-Only) | 1,480 rows (1,470 unique personnel) | Static Snapshot | External Benchmark Dataset |
| `data/processed/personnel_master.csv` | **Derived Pseudonymous Master** | Cleaned HR Attributes | 1,470 rows | Baseline | Derived from `HR_Analytics.csv` (Mapped to `P-000001` - `P-001470`) |
| `data/synthetic/deployment/deployment_records.csv` | **Synthetic Development Data** | Operational Logs | 4,715 records | 12 Months (2025-01 to 2025-12) | SAATHI Deterministic Scenario Engine (`SEED=42`) |
| `data/synthetic/leave/leave_history.csv` | **Synthetic Development Data** | Leave History | 4,687 records | 12 Months (2025-01 to 2025-12) | SAATHI Deterministic Scenario Engine (`SEED=42`) |
| `data/synthetic/workload/workload_records.csv` | **Synthetic Development Data** | Duty & Rest Metrics | 17,640 records | 12 Months (1,470 personnel x 12 mo) | SAATHI Deterministic Scenario Engine (`SEED=42`) |
| `data/synthetic/wellness/wellness_surveys.csv` | **Synthetic Development Data** | Voluntary Check-ins | 17,640 records | 12 Months (1,470 personnel x 12 mo) | SAATHI Deterministic Scenario Engine (`SEED=42`) |
| `data/synthetic/behavioral/behavioral_records.csv` | **Synthetic Development Data** | Organizational Shifts | 17,640 records | 12 Months (1,470 personnel x 12 mo) | SAATHI Deterministic Scenario Engine (`SEED=42`) |
| `data/processed/integrated_longitudinal.parquet` | **Integrated ML Training Set** | Multi-Signal & Baselines | 17,640 rows (137 features) | 12 Months | Longitudinal Feature Engineering Pipeline |

> **IMPORTANT DISCLAIMER**: The operational, workload, leave, wellness, and behavioral records are synthetic data generated for development, demonstration, and model prototyping. They do not represent actual CRPF personnel records.

---

## 2. Ethical Policy & Attrition Segregation

1. **Non-Equivalence of Attrition**:
   - The raw HR dataset contains an `Attrition` field representing historical employment termination / turnover.
   - Attrition is strictly **segregated** as an organizational HR statistic and is **never** used as a ground truth or proxy for clinical stress, mental health, burnout, or psychological fitness.
2. **Strict Surveillance Exclusion**:
   - SAATHI contains zero facial recognition, voice stress analysis, location tracking, camera surveillance, private communication monitoring, or social media scraping.
   - All behavioral indicators represent non-invasive organizational rhythm deviations (e.g. shift irregularity, routine deviation, duty delta).

---

## 3. Synthetic Simulation Scenarios

The synthetic generator simulates 6 deterministic and semi-stochastic occupational scenarios:

- **Scenario A (Stable Operation - 50%)**: Regular duty hours (170-190 hrs/mo), adequate rest (80-100 hrs/mo), regular leave every 60-90 days, stable voluntary wellness ratings (4-5/5) $\rightarrow$ Expected Priority: `GREEN`.
- **Scenario B (High Tempo - 15%)**: Temporary surges in duty hours (210-230 hrs/mo), overtime (25-45 hrs/mo), night shifts (5-8/mo), moderate fatigue $\rightarrow$ Expected Priority: `YELLOW`.
- **Scenario C (Extended Deployment - 12%)**: Extended deployment to remote/difficult terrain outposts, hardship level 4-5, delayed leave cycle (>120 days) $\rightarrow$ Expected Priority: `YELLOW / ORANGE`.
- **Scenario D (Cumulative Strain - 10%)**: Sustained high duty hours (230-260 hrs/mo), repeated night shifts (8-14/mo), consecutive duty days (10-15), declining wellness check-ins $\rightarrow$ Expected Priority: `ORANGE / RED`.
- **Scenario E (Recovery & Rebound - 8%)**: Initial high tempo (Months 2-5) followed by authorized recovery leave (Month 6) and stabilized rest, demonstrating priority reduction over time $\rightarrow$ Expected Priority: `YELLOW/ORANGE` $\rightarrow$ `GREEN`.
- **Scenario F (Resilient Noise / False-Alarm Resistance - 5%)**: Workload surge in Months 6-7, but personnel maintains high voluntary wellness ratings and recovery, demonstrating false-positive resistance $\rightarrow$ Expected Priority: `GREEN / light YELLOW`.

---

## 4. Personal Baseline Calculation Schema

The Personal Baseline Engine (`ml/baseline/personal_baseline.py`) computes:
1. **Rolling Historical Mean & Std**: Calculated over prior window $W=4$ months, shifted by 1 period so current period $T$ uses only periods up to $T-1$.
2. **Percentage Deviation**: $\Delta \% = \frac{x_T - \mu_{T-1}}{\mu_{T-1} + \epsilon} \times 100$
3. **Personal Z-Score**: $z = \frac{x_T - \mu_{T-1}}{\sigma_{T-1}}$
4. **Cold-Start Handling**: For personnel with $<3$ months of history, population-wide priors are used as fallback, `baseline_available` is flagged `False`, and model confidence is discounted.

---

## 5. Non-Leaking Predictive Target Horizon

To prevent circular target leakage, features at observation month $T$ predict the **Welfare Support Priority at month $T+1$**:
- Target Variable: `target_support_priority_next_month` (`GREEN`, `YELLOW`, `ORANGE`, `RED`)
- Target Score: `target_support_score_next_month` ($0 - 100$)
- Prediction Horizon: 1 Month Forward
- Time-Aware Splits:
  - **Training Set**: Months 1–7 (predicting Months 2–8) $\rightarrow$ 10,290 samples
  - **Validation Set**: Months 8–9 (predicting Months 9–10) $\rightarrow$ 2,940 samples
  - **Test Set**: Months 10–11 (predicting Months 11–12) $\rightarrow$ 2,940 samples
