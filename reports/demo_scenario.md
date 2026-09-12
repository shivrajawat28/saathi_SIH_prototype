# SAATHI — Judge & Evaluator Demonstration Scenario Guide

**SIH Problem Statement 26186:** AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**Target Organization:** Ministry of Home Affairs | CRPF, Police II Division  
**Canonical Demo Candidate:** `P-000013` (Support Score 88.1, RED Tier)  
**Fallback High-Strain Candidate:** `P-000081` (Support Score 88.0, RED Tier)  
**Stable Rhythm Comparison:** `P-000001` (Support Score 5.0, GREEN Tier)  
**Environment Status:** Demo Environment — Synthetic Personnel Telemetry (No Real Personnel Records Represented)  

---

## 1. Demo Scenario Overview

Personnel **`P-000013`** presents a canonical longitudinal strain progression pattern ideal for demonstrating SAATHI's non-punitive, early-intervention decision support:

```text
Months 1–3:  GREEN   (Stable operational rhythm: ~185h duty, 1–4 night shifts, ~75h rest, intensity 3)
Months 4–5:  YELLOW  (Emerging operational strain: >230h duty, 9–10 night shifts, rest drops to ~40h, intensity 5)
Months 6–8:  ORANGE  (Elevated cumulative burden: >245h duty, 11–13 night shifts, persistent leave latency)
Months 9–12: RED     (Priority Welfare Review: 261.2h duty, 14 night shifts, 38.3h rest, 302 days since leave)
```

---

## 2. Step-by-Step Judge Walkthrough Flow

```text
STEP 1: LOGIN & RBAC AUTHENTICATION
  • Navigate to http://localhost:5173/login
  • Click the "Welfare Officer" Quick Demo button (Auto-fills: welfare_officer / welfare123)
  • Click "Sign In to SAATHI"
  • Observe immediate authentication and redirect to Welfare Officer Dashboard.

STEP 2: BATCH TRIAGE & SPOTTING AT-RISK PERSONNEL
  • On the Welfare Dashboard, view KPI summary cards:
    - Total Monitored: 1,470 (Pseudonymous Roster)
    - Proactive Automated Alerts: 3 Active Emerging Concerns
  • Locate "P-000013" in the Priority Personnel triage table (Score: 88.1, Tier: RED).
  • Click "Inspect P-000013 (RED 88.1)" or row in triage table.

STEP 3: OPERATIONAL CONTEXT & DEPLOYMENT EXPOSURE
  • Review the Operational Deployment, Transfer & Readiness Context section:
    - Deployment Status: Active Field Deployment (Intensity Level: 5 / 5)
    - Cumulative Deployment Exposure: 8 of 12 Months Deployed (67% Field Exposure)
    - Movement & Transfer Indicator: Moderate Transfer Frequency
    - Training & Readiness: Annual training modules completed
    - Proactive Alert: Emerging strain pattern detected (Duty surge, night shifts, leave gap)

STEP 4: 12-MONTH LONGITUDINAL TRAJECTORY
  • Observe the sequential 12-month Composed Chart (Duty Hours vs. Rest Hours with Support Priority line).
  • Note the transition from stable baseline in early months to sustained operational overload in Months 6–12.
  • Toggle between "Duty & Shifts", "Support Score", and "Rest & Recovery".

STEP 5: PERSONAL BASELINE COMPARISON
  • Inspect the Personal Baseline Deviation card comparing the individual against their own historical norm:
    - Monthly Duty Hours: 261.2 hrs (vs. Historical Baseline ~184 hrs -> +42% surge)
    - Night Shifts: 14 shifts (vs. Baseline ~2 shifts -> +600% surge)
    - Rest & Recovery: 38.3 hrs (vs. Baseline 80.0 hrs -> -52% deficit)
    - Leave Latency: 302 days elapsed since last restorative leave.
    - Causal Window: Strictly t ≤ T-1 historical baseline (zero future leakage).

STEP 6: "WHY DID THIS SCORE CHANGE?" (TRANSPARENT EXPLAINABILITY)
  • Review the Transparent Factor Attribution list powered by the locked tree model:
    ↑ Elapsed duration since previous leave: +19.6% impact
    ↑ Operational tempo & intensity level: +16.7% impact
    ↑ Total monthly workload index: +14.5% impact
  • Emphasize to judges: Plain, non-clinical operational indicators without medical diagnosis.

STEP 7: RULE-BASED DETERMINISTIC WELFARE RECOMMENDATIONS
  • Review system recommendations:
    - [HIGH] Recovery Leave: Extended period (302 days) without authorized rest.
    - [HIGH] Workload Review: Operational tempo exceeding historical baseline limits.
    - [HIGH] Welfare Check-in: Authorized welfare officer conversational review.

STEP 8: WHAT-IF WELFARE SIMULATOR (MODEL-BASED SCENARIO SIMULATION)
  • In the "What-If Welfare Simulator" panel, apply the Canonical Preset or adjust sliders:
    - Reduce Duty Hours: -40 hrs (261.2 → 221.2 hrs)
    - Reduce Night Shifts: -8 shifts (14 → 6 shifts)
    - Grant Restorative Leave: +3 days
    - Curtail Overtime: -10 hrs
  • Click "Simulate Operational Impact".
  • Observe instantaneous live API response:
    - Current Support Score: 88.1 (RED)
    - Projected Model Response: 80.3 (Projected Delta: -7.8 pts)
  • Transparent Safeguard: "Projected model response — not a causal guarantee. Simulation does not modify persistent records."

STEP 9: HUMAN-IN-THE-LOOP WELFARE ACTION LOGGING
  • Click "Record Welfare Action" button.
  • Select Intervention Type: "Workload Review & Scheduled Rest".
  • Enter Action Summary: "Scheduled 5 days compensatory rest and reallocated night patrol rota to second platoon."
  • Click "Record Welfare Action".
  • Verify new entry appears in Intervention History.

STEP 10: CLOSED-LOOP OUTCOME TRACKING
  • In the intervention card, click "Record Follow-up Outcome".
  • Select Outcome: "IMPROVED".
  • Enter Follow-up Notes: "Personnel completed rest window; duty hours stabilized to normal platoon rotation."
  • Submit and observe status updating to "RESOLVED / IMPROVED".

STEP 11: IMMUTABLE AUDIT TRAIL
  • Logout and switch to "Admin" role (admin / admin123).
  • Navigate to Admin & Audit Trail.
  • Verify immutable timestamped log entries for every step executed:
    - VIEW_BATCH_TRIAGE (welfare_officer)
    - VIEW_PERSONNEL_TIMELINE (personnel:P-000013)
    - RUN_WHATIF_SIMULATION (personnel:P-000013)
    - CREATE_INTERVENTION (personnel:P-000013)
    - RECORD_OUTCOME (personnel:P-000013)
```

---

## 3. Alternative Role Demonstrations

### Commander Experience (`commander` / `commander123`)
1. Login as Commander.
2. View aggregate readiness: 86% stable rhythm across total strength (1,470 personnel).
3. Inspect unit-level tier distribution and division breakdown (Operations, Communications & Technology, Administration & Welfare).
4. **Key Security Point for Judges:** Commander portal contains **zero individual survey text**, zero private check-in narratives, and restricted individual identity lookups.

### Personnel Self-Service Portal (`personnel_p13` or `officer_p1`)
1. Login as Personnel P-000013 (or P-000001).
2. View individual operational calendar and recorded rest hours.
3. Submit a **Voluntary Monthly Wellness Check-in** (Sleep Quality: 4/5, Fatigue Level: 2/5, Work Stress: 2/5).
4. Read privacy disclosure: "Check-ins are voluntary, non-diagnostic, and used solely for supportive welfare planning."

---

## 4. Summary Table of Demo Credentials

| Role | Username | Password | Default Landing Page | Primary Capability |
| :--- | :--- | :--- | :--- | :--- |
| **Welfare Officer** | `welfare_officer` | `welfare123` | `/welfare` | Individual deep dive, predictions, simulator, interventions |
| **Commander** | `commander` | `commander123` | `/commander` | Aggregate unit distribution, readiness KPI (no private surveys) |
| **Personnel (Canonical Demo)** | `personnel_p13` | `personnel123` | `/portal` | Confidential voluntary check-in & own operational profile (`P-000013`) |
| **Personnel (Baseline Demo)** | `officer_p1` | `personnel123` | `/portal` | Confidential voluntary check-in & own operational profile (`P-000001`) |
| **Welfare Analyst** | `analyst` | `analyst123` | `/analyst` | Anonymized division metrics & priority tier charts |
| **Administrator** | `admin` | `admin123` | `/admin` | Complete immutable audit trail & user role management |
