# SAATHI: Synthetic Data v2 Specification & Noise Modeling Report

## 1. Motivation for Synthetic Data Version 2 (`data/synthetic_v2/`)

While Synthetic v1 successfully modeled 6 occupational archetypes, its linear feature-to-target coherence ($r \approx 0.80$) made high-tempo cumulative strain more predictable than real human telemetry. 

To provide a more realistic stress-test environment, **Synthetic Data v2** was generated in `data/synthetic_v2/` without modifying the original v1 datasets.

---

## 2. Key Realistic Noise & Behavioral Modifications in v2

| Feature Domain | Synthetic v1 (Baseline Prototype) | Synthetic v2 (Robust Stress-Test) | Operational Rationale |
|---|---|---|---|
| **Duty & Rest Hours** | Fixed monthly averages ($\pm 4$ hrs) | Gaussian telemetry measurement jitter ($\pm 6$ hrs) + random overtime surges | Real shift rosters experience irregular duty extensions and logging errors. |
| **Cumulative Fatigue Debt** | Instantaneous monthly calculation | Multi-month **fatigue debt accumulator** ($F_{\text{debt}} \leftarrow F_{\text{debt}} + \Delta_{\text{duty}} - \text{Recovery}$) | Chronic strain accumulates non-linearly and persists after heavy deployments end. |
| **Voluntary Check-Ins** | 92% uniform completion | **15% variable missingness** + compliance distribution ($40\%\text{--}98\%$) | Officers with high workload often skip voluntary wellness apps. |
| **Reporting Bias** | Direct accurate reporting | **25% Stoicism** (under-reporting strain) & **15% Somatic Sensitivity** | Stigma or culture in uniformed forces frequently leads to under-reported stress. |
| **Individual Resilience** | Uniform scaling | Non-linear individual resilience factors ($\sim \mathcal{N}(3.0, 0.8)$) | Different personnel possess different psychological and physiological coping capacities. |
| **Delayed Recovery Onset** | Instant recovery post-leave | Delayed rebound (1–2 months lag for full autonomic recovery) | High operational exhaustion requires prolonged rest before wellness scores return to baseline. |

---

## 3. Directory Layout for Synthetic v2

```
data/synthetic_v2/
├── deployment/
│   └── deployment_records.csv
├── leave/
│   └── leave_history.csv
├── workload/
│   └── workload_records.csv
├── wellness/
│   └── wellness_surveys.csv
└── behavioral/
    └── behavioral_records.csv
```

> **Data Integrity**: All original v1 files in `data/synthetic/` and `data/official_hr/` remain untouched.
