# SAATHI — SIH Problem Statement 26186 Alignment Audit

**SIH Problem Statement 26186:** AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**Organization:** Ministry of Home Affairs  
**Department:** Central Reserve Police Force (CRPF), Police II Division  
**System:** SAATHI (System for AI-Assisted Telemetry & Holistic Intervention)  
**Audit Date:** Phase 6 Polish & Final Verification  

---

## Executive Summary

This document provides a 20-point requirement-by-requirement audit of Project SAATHI against the official Smart India Hackathon (SIH) Problem Statement 26186 requirements, constraints, ethical boundaries, and operational safeguards.

---

## 20-Point Requirement Compliance Matrix

| # | Requirement | Current Implementation | Evidence / File | Status | Required Action / Audit Note |
| :- | :--- | :--- | :--- | :---: | :--- |
| **1** | **HR & Operational Indicators** (Leave patterns, duty schedules, workload trends) | Longitudinal monthly records tracking duty hours, night shifts, overtime, rest, and leave latency over 12 months with causal baseline ($t \le T-1$). | `data/processed/integrated_longitudinal.parquet`<br>`backend/app/api/personnel.py` | **COMPLIANT** | Fully integrated across ML, database, and UI. |
| **2** | **Deployment History** | Operational deployment flags, hardship intensity ratings (Levels 1–5), and cumulative field exposure tracking. | `backend/app/api/personnel.py`<br>`frontend/src/pages/PersonnelDetailPage.tsx` | **COMPLIANT** | Exposed in Personnel Detail "Operational Deployment Context". |
| **3** | **Transfer Frequency** | Role tenure and movement indicators tracking years in post and supervisor rotation frequency. | `backend/app/models/personnel.py`<br>`frontend/src/pages/PersonnelDetailPage.tsx` | **COMPLIANT** | Displayed non-clinically as occupational background context. |
| **4** | **Training Commitments** | Annual training cadence tracking structured modules completed without interfering with validated ML pipeline. | `backend/app/models/personnel.py`<br>`backend/app/schemas/personnel.py` | **COMPLIANT** | Displayed in Personnel Detail context card. |
| **5** | **Optional Wellness / Self-Reporting** | Confidential, voluntary 6-metric check-in (sleep quality, fatigue, mood, balance) restricted from commanders. | `backend/app/api/wellness.py`<br>`frontend/src/pages/PersonnelPortalPage.tsx` | **COMPLIANT** | Strictly voluntary with zero diagnostic labels. |
| **6** | **Voluntary Telemetry Safeguards** | Zero compulsory biometric surveillance, zero keystroke logging, zero camera monitoring, zero GPS tracking, zero private message monitoring. | `tests/test_data_quality.py`<br>`frontend/src/components/EthicsModal.tsx` | **COMPLIANT** | Enforced by automated security assertions. |
| **7** | **Behavioral Pattern Detection** | Temporal feature engineering detecting deviations from individual historical mean ($\Delta$, %, $z$-score). | `ml/src/features/baseline_engine.py`<br>`backend/app/ml/adapter.py` | **COMPLIANT** | Causal window $t \le T-1$ strictly maintained. |
| **8** | **Risk / Support-Priority Assessment** | Non-clinical Support Priority Score (0–100) mapped to 4 actionable operational tiers: GREEN, YELLOW, ORANGE, RED. | `backend/app/services/prediction_service.py`<br>`frontend/src/components/ScoreMeter.tsx` | **COMPLIANT** | Platt calibrated probabilities; non-medical terminology. |
| **9** | **Deterministic Welfare Recommendations** | Rule-based engine mapping high-impact signals to non-punitive welfare suggestions (rest, rotation, check-in). | `backend/app/services/recommendation_service.py`<br>`frontend/src/components/RecommendationList.tsx` | **COMPLIANT** | Deterministic, transparent, and non-disciplinary. |
| **10** | **Proactive Early Welfare Intervention** | Closed-loop intervention logging enabling authorized officers to record recovery actions and follow-up outcomes. | `backend/app/api/interventions.py`<br>`frontend/src/components/InterventionModal.tsx` | **COMPLIANT** | Lifecycle tracking (OPEN → IN_PROGRESS → RESOLVED). |
| **11** | **Workload Balancing & What-If Simulator** | Interactive scenario simulator projecting model response under reduced shifts/duty without modifying records. | `backend/app/services/simulation_service.py`<br>`frontend/src/components/WhatIfSimulator.tsx` | **COMPLIANT** | Model-based projection; non-causal disclaimer visible. |
| **12** | **Role-Based Operational Dashboards** | Distinct interfaces tailored for Welfare Officers, Commanders, Analysts, Administrators, and Personnel. | `frontend/src/pages/`<br>`backend/app/core/permissions.py` | **COMPLIANT** | 5 segregated RBAC roles enforced in backend & frontend. |
| **13** | **Responsive Personnel Portal** | Mobile-friendly web interface allowing personnel to view own schedule and submit confidential check-ins. | `frontend/src/pages/PersonnelPortalPage.tsx` | **COMPLIANT** | Responsive across desktop, tablet, and mobile (390px). |
| **14** | **Predictive Behavioral Analytics** | Random Forest high-risk classifier trained on temporal features to forecast emerging strain 1 month forward ($T+1$). | `ml/models/support_priority_model.joblib`<br>`ml/models/model_metadata.json` | **COMPLIANT** | Locked, validated architecture. |
| **15** | **Non-Clinical Stress / Welfare Modelling** | Honest framing: Decision support for welfare resource prioritization; zero medical/psychiatric diagnosis. | `reports/demo_scenario.md`<br>`frontend/src/components/Navbar.tsx` | **COMPLIANT** | Verified zero forbidden clinical terms in UI/API. |
| **16** | **Proactive Automated Welfare Alerts** | Priority surge and recovery deficit notifications for authorized Welfare Officers; aggregate unit alerts for Commanders. | `frontend/src/pages/WelfareDashboardPage.tsx`<br>`frontend/src/pages/PersonnelDetailPage.tsx` | **COMPLIANT** | Clear, non-stigmatizing alert indicators. |
| **17** | **Strict Anonymization & Pseudonymity** | Roster mapped to pseudonymous identifiers (`P-000001`–`P-001470`); zero real PII (names, Aadhaar, phones). | `data/processed/personnel_master.csv`<br>`backend/app/models/personnel.py` | **COMPLIANT** | Synthetic demo environment banner visible. |
| **18** | **Transparent Explainability (XAI)** | Tree-based factor attribution explaining why score changed relative to personal historical baseline. | `backend/app/ml/adapter.py`<br>`frontend/src/components/FactorAttributionList.tsx` | **COMPLIANT** | Identifies top contributing occupational factors. |
| **19** | **Human-in-the-Loop Decision Making** | System acts as decision support aid; all welfare actions, duty adjustments, and follow-ups decided by human officers. | `frontend/src/components/EthicsModal.tsx`<br>`backend/app/services/recommendation_service.py` | **COMPLIANT** | Zero automated punitive or employment decisions. |
| **20** | **Immutable Audit & Ethical Safeguards** | Tamper-evident audit logging for every authentication, prediction, simulation, intervention, and data query. | `backend/app/services/audit_service.py`<br>`frontend/src/pages/AuditLogsPage.tsx` | **COMPLIANT** | Admin-restricted audit trail with IP & timestamp. |

---

## Scientific & Contextual Honesty Summary

1. **Non-Clinical Framing:** SAATHI never uses medical diagnosis terms (*"Depression"*, *"Mental Illness"*, *"Psychological Failure"*, *"Unfit for Duty"*). It produces a non-clinical **Welfare Support Priority Score (0–100)** to guide human outreach.
2. **Synthetic Data Disclosure:** Clearly labeled as a prototype demo environment operating on synthetic longitudinal telemetry derived from open benchmark distributions. No real CRPF personnel records are represented.
3. **Model-Based Projections:** What-If scenario simulations are explicitly labeled as model projections, avoiding over-claiming causal inference or guarantees.
4. **Psychological Safety:** Commanders and Analysts receive aggregate and anonymized metrics only; subjective check-in narratives and individual prediction triggering are restricted to authorized Welfare Officers and individual personnel.
