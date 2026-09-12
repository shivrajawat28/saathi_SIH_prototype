# SAATHI — Phase 5 Initial System Audit & Hardening Plan

**SIH Problem Statement 26186:** AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**Organization:** Ministry of Home Affairs | CRPF, Police II Division  
**Date:** September 2026  
**Auditor:** Lead Systems & Security Auditor  

---

## 1. Discovered System Architecture

### 1.1 ML & Telemetry Engine (Locked Foundation)
* **Model Pipeline:** Balanced Random Forest Classifier with Platt (Sigmoid) Probability Calibration (`ml/models/support_priority_model.joblib`).
* **Personal Historical Baseline Engine:** Computes running baseline over causal window $t \le T-1$ to evaluate relative deviations in duty hours, night shifts, rest hours, and leave latency.
* **Output Semantics:**
  - **Welfare Support Priority Score:** $100 \times \text{calibrated probability of high-risk operational welfare state}$ (Continuous range: 0.0 to 100.0).
  - **Prediction Reliability:** Composite index weighting model certainty, data completeness, and baseline history maturity (0.0 to 1.0).
  - **Tiers:** `GREEN` ($< 30$), `YELLOW` ($30 - 54.9$), `ORANGE` ($55 - 74.9$), `RED` ($\ge 75$), and `INSUFFICIENT_DATA` ($C < 0.35$).
* **Explainability:** SHAP/Tree-feature attributions translated into non-clinical, operational language.
* **Deterministic Rule Engine:** Generates rule-based non-punitive suggestions (`WORKLOAD_REVIEW`, `RECOVERY_LEAVE`, `WELFARE_CHECK_IN`, `SCHEDULE_ADJUSTMENT`, `FOLLOW_UP_ASSESSMENT`).

### 1.2 Backend API & Database
* **Framework:** FastAPI with SQLAlchemy 2.0 (SQLite for local rapid demo, PostgreSQL compatible).
* **Security & RBAC:** JWT Bearer authentication (HMAC-SHA256), bcrypt password hashing, 5 distinct system roles (`ADMIN`, `WELFARE_OFFICER`, `COMMANDER`, `ANALYST`, `PERSONNEL`).
* **Core Services:**
  - `auth_service.py`: Authentication, token generation, user management.
  - `prediction_service.py`: Pipeline execution, triage dashboard, database persistence, and audit logging.
  - `recommendation_service.py`: Deterministic welfare logic.
  - `simulation_service.py`: Counterfactual what-if scenario testing without altering permanent records.
  - `intervention_service.py`: Human intervention logging and closed-loop outcome tracking (`IMPROVED`, `UNCHANGED`, `ESCALATED`).
  - `audit_service.py`: Immutable chronological security and operational audit trail.

### 1.3 Frontend Architecture
* **Stack:** React 18.3.1, TypeScript 5.7.3, Vite 6.1.0, Tailwind CSS 3.4.17, Recharts 2.15.1, Lucide React, Axios.
* **Role Experiences:**
  - **Welfare Officer:** Batch triage, individual 12-month trajectory, baseline comparison, factor attributions, what-if simulator, intervention logging, outcome evaluation.
  - **Commander:** Unit-level aggregate distribution, operational readiness index, division breakdown (strictly isolated from private subjective survey text).
  - **Analyst:** Anonymized division metrics and tier percentages (no direct identity lookup).
  - **Personnel:** Confidential voluntary wellness check-in, personal duty and recovery overview.
  - **Admin:** Immutable system audit trail and user management.

---

## 2. Previous Test Claims Baseline

* **Backend Test Suite:** 37 / 37 passed (`pytest backend/tests/ tests/ -v`).
* **Frontend Test Suite:** 14 / 14 passed (`npm test` in `frontend/`).
* **Production Build:** Clean TypeScript & Vite build.

---

## 3. High-Priority Risk Vectors to Audit

1. **RBAC Adversarial Bypass & IDOR (P0):**
   - Can a `PERSONNEL` user access records or predictions of another `PERSONNEL` by changing `personnel_id` in API requests?
   - Can a `COMMANDER` bypass restrictions to read raw subjective survey text or individual personnel records?
   - Can an `ANALYST` perform direct identity lookups?
   - Can unauthorized users trigger interventions or modify outcomes?
2. **Simulation Service Bounds & Edge Cases (P1):**
   - Do extreme numerical inputs or negative deltas in what-if simulations crash the service or produce invalid probabilities?
   - Are projected scores properly clamped within $[0, 100]$?
3. **Data Completeness & Cold-Start Gate (P1):**
   - Does a record with missing core telemetry gracefully trigger `INSUFFICIENT_DATA` rather than a misleading zero score?
4. **Secrets & Privacy Audit (P0/P1):**
   - Are database passwords, JWT secrets, or private keys committed anywhere?
   - Do error messages or audit logs leak sensitive payloads or passwords?
5. **Clean Environment Startup & Docker Reproducibility (P1/P2):**
   - Can the application start cleanly from scratch without local artifacts or ambient state?
6. **Frontend UX & Resilience (P2):**
   - Does the UI handle network timeouts, 401 token expirations, and missing telemetry without crashing or rendering blank screens?

---

## 4. Phase 5 Hardening & Verification Roadmap

* [x] Step 1: Complete Repository & Architectural Audit (`reports/phase5_initial_audit.md`)
* [ ] Step 2: Clean-Environment Startup & Docker Verification
* [ ] Step 3: Authentication Security & Token Expiry Audit
* [ ] Step 4: RBAC Adversarial Penetration Testing (`reports/rbac_adversarial_test.md`)
* [ ] Step 5: IDOR & Object-Level Authorization Penetration Test
* [ ] Step 6: Privacy & Confidentiality Audit (`reports/security_audit.md`)
* [ ] Step 7: Secrets & Credentials Audit
* [ ] Step 8: API Contract vs Implementation Audit (`reports/api_contract_audit.md`)
* [ ] Step 9: Data Validation & Edge Case Robustness Testing
* [ ] Step 10: ML Inference & Personal Baseline Temporal Leakage Audit (`reports/ml_integration_audit.md`)
* [ ] Step 11: Score Semantics & Reliability Disclaimers Verification
* [ ] Step 12: Data Completeness Gate Verification
* [ ] Step 13: Explainability & Factor Attribution Consistency Audit
* [ ] Step 14: What-If Counterfactual Simulator Hardening
* [ ] Step 15: Intervention Lifecycle & Closed-Loop Outcome Verification
* [ ] Step 16: Audit Logging & Immutability Verification
* [ ] Step 17: Frontend UX, Accessibility & Cross-Role Review (`reports/frontend_ux_audit.md`)
* [ ] Step 18: Demo Scenario & Fallback Candidate Verification (`reports/demo_scenario.md`)
* [ ] Step 19: Comprehensive System Test Execution & Final Verification Matrix (`reports/phase5_final_verification.md`)
