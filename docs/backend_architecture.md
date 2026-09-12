# SAATHI Backend Architecture & System Design Specification

## 1. Overview & Project Intent

**SAATHI** is an AI-powered Welfare Support Decision System designed for uniformed personnel.
The system is explicitly **NOT a medical diagnosis system**; it does not diagnose depression, mental illness, or psychological fitness, nor does it conduct invasive surveillance.

Instead, SAATHI provides an objective **Welfare Support Priority** (`GREEN`, `YELLOW`, `ORANGE`, `RED`) and a continuous **Welfare Support Score ($0\text{--}100$)** to authorized welfare officers to enable proactive, non-punitive occupational support and human-led interventions.

---

## 2. Core System Architecture Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                         CLIENT / CONSUMERS                                        |
|  (Welfare Officer Portal, Commander Dashboard, Analytical Tools, Individual Personnel Portal)      |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  │ HTTPS / REST (JSON + JWT)
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                                     FASTAPI APPLICATION GATEWAY                                   |
|  - CORS Middleware & Security Headers        - Request Validation (Pydantic v2)                   |
|  - JWT Authentication & Session Resolver     - Strict Role-Based Access Control (RBAC)            |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                                          ROUTERS & APIS                                           |
|  ├── /api/v1/auth          (Login, Token Refresh, Identity /me)                                   |
|  ├── /api/v1/personnel     (Pseudonymous Roster, Operational Profiles, Longitudinal History)      |
|  ├── /api/v1/predictions   (Predict Welfare Support Priority, Factor Attribution, Batch Triage)   |
|  ├── /api/v1/wellness      (Voluntary Check-ins, Self-Reported Metrics)                           |
|  ├── /api/v1/recommendations (Deterministic Decision-Support Action Suggestions)                  |
|  ├── /api/v1/interventions (Welfare Actions Recording & Closed-Loop Outcome Tracking)             |
|  ├── /api/v1/simulations   (What-If Scenario Simulation API Contract)                             |
|  ├── /api/v1/analytics     (Aggregated Commander / Analyst Trends without Sensitive PII)         |
|  └── /api/v1/audit         (Immutable System Audit Logs)                                          |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                                      APPLICATION SERVICES LAYER                                    |
|  ├── PredictionService     ──► Wraps locked ML pipeline (Random Forest + Platt Calibration)       |
|  ├── BaselineService       ──► Causal Personal Baseline Engine (t <= T-1 historical rolling stats) |
|  ├── ExplanationService    ──► SHAP & Feature Attribution to Human-Readable Factor Driver Mapping  |
|  ├── RecommendationService ──► Deterministic Rule-Based Welfare Decision Support Engine           |
|  ├── InterventionService   ──► Action Lifecycle & Outcome Tracking (Improved, Unchanged, Escalated)|
|  ├── SimulationService     ──► Counterfactual Workload/Recovery Scenario Projections              |
|  └── AuditService          ──► Mandatory Auditing for all sensitive inspections & interventions  |
+---------------------------------------------------------------------------------------------------+
                               │                                                   │
                               ▼                                                   ▼
+-----------------------------------------------+   +-----------------------------------------------+
|             LOCKED ML ADAPTER & ENGINE        |   |           POSTGRESQL / SQLALCHEMY 2.X         |
|  - ml/models/support_priority_model.joblib    |   |  - Normalized Relational Storage              |
|  - ml/baseline/personal_baseline.py           |   |  - Longitudinal Data Tables (Workload, Leave) |
|  - ml/explainability/explainer.py             |   |  - Audit Logs & Pseudonymous Identity Store   |
+-----------------------------------------------+   +-----------------------------------------------+
```

---

## 3. Database Design & Schema Architecture

The database utilizes a normalized schema with strict privacy-preserving pseudonymity:

```
[ users ] 1──* [ user_roles ] *──1 [ roles ]
   │
   ▼ (Optional link for personnel users)
[ personnel ] (personnel_id: P-000001)
   ├── 1──1 [ hr_profiles ] (Demographics, Job Role, Experience, Education)
   ├── 1──* [ deployment_records ] (Duration, Hardship, Intensity, Terrain)
   ├── 1──* [ leave_records ] (Type, Duration, Days Since Previous Leave)
   ├── 1──* [ workload_records ] (Duty Hours, Overtime, Night Shifts, Rest Hours)
   ├── 1──* [ wellness_records ] (Voluntary Check-ins: Sleep, Fatigue, Strain)
   ├── 1──* [ behavioral_records ] (Routine Deviation, Attendance & Schedule Changes)
   ├── 1──* [ predictions ] (Support Score, Priority Tier, Reliability, Completeness)
   │          ├── 1──* [ prediction_explanations ] (Top Contributing Factors)
   │          └── 1──* [ welfare_recommendations ] (Suggested Non-Disciplinary Actions)
   └── 1──* [ interventions ] (Welfare Action Taken, Notes, Date, Responsible Officer)
              └── 1──* [ intervention_outcomes ] (Improved, Unchanged, Escalated)

[ audit_logs ] (User ID, Role, Action, Target Resource, Timestamp, IP Address, Status)
```

---

## 4. Role-Based Access Control (RBAC) Matrix

| Resource / Endpoint | `ADMIN` | `WELFARE_OFFICER` | `COMMANDER` | `ANALYST` | `PERSONNEL` |
|---|---|---|---|---|---|
| User & Role Management (`/auth/users`) | Full Access | No Access | No Access | No Access | No Access |
| View System Audit Logs (`/audit/logs`) | Full Access | No Access | No Access | No Access | No Access |
| View Assigned Personnel Master (`/personnel/`) | Full Access | Full (Assigned) | Restricted List | Pseudonymized Only | Self Only |
| View Detailed Telemetry & Longitudinal Data | Full Access | Full (Assigned) | Workload Only | Aggregated Only | Self Only |
| View Raw Voluntary Wellness Surveys | No Access | Full (Assigned) | **Denied (Privacy)** | **Denied (Privacy)** | Self Only |
| Generate & View Predictions & Explanations | Full Access | Full Access | Aggregate / Tier Only | Aggregated Only | Self (Score Only) |
| Create & Update Welfare Interventions | Full Access | Full Access | View Action Status | View Anonymized Counts | No Access |
| Submit Voluntary Wellness Check-in | No Access | No Access | No Access | No Access | Self Only |
| Run Counterfactual What-If Simulation | Full Access | Full Access | Full Access | Anonymized | Self Only |

---

## 5. Information Flow: Prediction Lifecycle

1. **Request**: Welfare Officer requests prediction for `P-000412`.
2. **Authorization**: RBAC validates officer credentials and assignment.
3. **Data Assembly**: Loads longitudinal history up to observation month $T$.
4. **Causal Baseline**: Executes `PersonalBaselineEngine` utilizing strictly $t \le T-1$ history.
5. **Quality Check**: Computes Data Completeness ($C$). If $C < 0.35$, returns `status: "INSUFFICIENT_DATA"`.
6. **ML Inference**: Feeds observation into locked Random Forest + Platt Calibration artifact.
7. **Score Derivation**:
   - $P_{\text{calibrated}}(\text{High-Risk})$
   - Continuous Support Score $S = 100 \times P_{\text{calibrated}}(\text{High-Risk})$
   - Priority Tier: `GREEN` ($S < 30$), `YELLOW` ($30 \le S < 55$), `ORANGE` ($55 \le S < 75$), `RED` ($S \ge 75$).
8. **Reliability Index**: Calibrates prediction reliability based on model certainty, completeness, and baseline availability.
9. **Explainability**: `WelfareExplainer` extracts top 3 contributing factors with direction and percentage contribution.
10. **Recommendations**: `RecommendationEngine` generates deterministic, non-disciplinary action options.
11. **Persistence & Audit**: Saves prediction record and writes an immutable entry to `audit_logs`.
12. **Response**: Returns structured decision-support JSON.

---

## 6. Security, Privacy & Ethical Guardrails

- **Zero Medical Diagnoses**: No clinical terms ("depressed", "mental illness", "unfit").
- **Zero Surveillance Vectors**: No camera feeds, facial analysis, voice stress, GPS tracking, or private message scraping.
- **Voluntary Wellness Privacy**: Raw voluntary survey details are strictly masked from Commanders and Analysts.
- **Closed-Loop Accountability**: Human welfare officers retain 100% authority for all reviews, interventions, and follow-ups.
