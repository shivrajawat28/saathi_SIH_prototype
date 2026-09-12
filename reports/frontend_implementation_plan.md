# SAATHI: Phase 4 Frontend Implementation Plan

## 1. Executive Summary

**Project:** SAATHI (AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces)  
**SIH Problem Statement:** 26186  
**Objective:** Build a production-grade, ethical, decision-support frontend interface connecting seamlessly to the validated FastAPI backend and locked ML foundation.

---

## 2. Detected Environment & Stack Selection

- **Backend:** FastAPI (Python 3.11/3.13), SQLAlchemy 2.x, PostgreSQL/SQLite (`saathi.db`), JWT Auth, RBAC, 37 passing backend tests.
- **ML Foundation (Locked):** Balanced Random Forest + Platt Sigmoid Calibration ($\tau = 0.50$), Causal Personal Baseline Engine ($t \le T-1$), SHAP/Feature attribution, Deterministic Recommendation Engine.
- **Frontend Stack Selected:**
  - **Framework:** React 18 + TypeScript (strict typing)
  - **Build Tool:** Vite (fast HMR and lightweight bundle)
  - **Styling:** Tailwind CSS (clean, calm, accessible, non-flashy design language)
  - **Icons:** Lucide React (standardized UI icons)
  - **Charts:** Recharts (responsive time-series, radar, and distribution visualizations)
  - **Routing:** React Router v6 (declarative protected routes + RBAC guards)
  - **State & Data Fetching:** React Context + Typed Axios API Client with JWT interceptors.

---

## 3. Discovered Backend API Endpoints

| Resource | Method & Path | Access Control | Frontend Usage |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST /api/v1/auth/login` | Public | Login credentials authentication |
| | `GET /api/v1/auth/me` | Authenticated | Fetch active user profile & permissions |
| | `POST /api/v1/auth/users` | `ADMIN` | Provision new system users |
| **Personnel** | `GET /api/v1/personnel/` | `ADMIN`, `WELFARE_OFFICER`, `COMMANDER`, `ANALYST`, `PERSONNEL` (own) | Personnel master directory |
| | `GET /api/v1/personnel/{id}` | Role authorized | Baseline HR and occupational traits |
| | `GET /api/v1/personnel/{id}/timeline` | Role authorized (Commander filtered) | 12-Month longitudinal telemetry |
| **Predictions** | `POST /api/v1/predictions/personnel/{id}` | `WELFARE_OFFICER`, `ADMIN`, `PERSONNEL` (own) | ML Support score, Reliability, SHAP factors, Recs |
| | `GET /api/v1/predictions/batch-triage` | `WELFARE_OFFICER`, `COMMANDER`, `ADMIN` | Ranked batch triage dashboard |
| **Interventions** | `POST /api/v1/interventions/` | `WELFARE_OFFICER`, `ADMIN` | Record human welfare action |
| | `GET /api/v1/interventions/personnel/{id}` | Role authorized | List intervention history |
| | `POST /api/v1/interventions/{id}/outcomes` | `WELFARE_OFFICER`, `ADMIN` | Record longitudinal outcome evaluation |
| **Simulations** | `POST /api/v1/simulations/personnel/{id}` | `WELFARE_OFFICER`, `COMMANDER`, `ADMIN` | What-If counterfactual scenario projection |
| **Analytics** | `GET /api/v1/analytics/commander-overview` | `COMMANDER`, `ANALYST`, `ADMIN`, `WELFARE_OFFICER` | Unit-level aggregate welfare metrics |
| **Wellness** | `POST /api/v1/wellness/check-in` | `PERSONNEL` | Confidential voluntary check-in submission |
| **Audit** | `GET /api/v1/audit/logs` | `ADMIN` | Immutable chronological security audit trail |

---

## 4. Required Pages & User Experience

```
[Login Screen (Quick Demo Role Switcher)]
   ├── Welfare Officer -> Welfare Dashboard -> Personnel Detail (Timeline, Score, Factors, What-If, Interventions, Outcomes)
   ├── Commander -> Aggregate Unit Dashboard (Readiness, Distributions, Trends - Zero Private Surveys)
   ├── Analyst -> Analytical Insights (Anonymized Trends & Breakdown)
   ├── Personnel -> Personal Portal (My Timeline, Voluntary Check-in, Privacy Notice)
   └── Admin -> User Provisioning & Immutable Audit Trail
```

1. **`LoginPage`**: Clean authentication with fast one-click demo credentials for judges.
2. **`WelfareDashboardPage`**: KPI summary cards, batch triage priority table with search/filters, department breakdown, recent interventions.
3. **`PersonnelDetailPage` (Centerpiece)**:
   - 12-Month interactive longitudinal timeline.
   - Continuous Welfare Support Priority Score ($0-100$) + Tier badge (GREEN/YELLOW/ORANGE/RED).
   - Prediction Reliability indicator & Data Completeness gauge.
   - Personal Historical Baseline vs. Current Observation comparison cards (Z-scores, % changes).
   - "Why Did This Score Change?" feature attribution section.
   - Deterministic Welfare Recommendations with actionable buttons.
   - Interactive What-If Counterfactual Simulator with real-time API projections.
   - Intervention modal & Closed-Loop Outcome recording history.
4. **`CommanderDashboardPage`**: Aggregated unit welfare distribution, tempo metrics, department health, zero sensitive individual survey text.
5. **`PersonnelPortalPage`**: Individual personnel view, confidential voluntary wellness submission form, clear privacy & non-diagnostic notices.
6. **`AdminAuditPage`**: User management & chronological security audit log inspection.
7. **`EthicsModal` & Global Privacy Indicator**: Explaining non-surveillance, non-medical status, and human-in-the-loop governance.

---

## 5. Integration Strategy & Directory Structure

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   ├── api/
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── personnel.ts
│   │   ├── predictions.ts
│   │   ├── interventions.ts
│   │   ├── simulations.ts
│   │   ├── analytics.ts
│   │   ├── wellness.ts
│   │   └── audit.ts
│   ├── types/
│   │   └── index.ts
│   ├── context/
│   │   └── AuthContext.tsx
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   ├── ProtectedRoute.tsx
│   │   ├── PriorityBadge.tsx
│   │   ├── ScoreMeter.tsx
│   │   ├── BaselineComparisonCard.tsx
│   │   ├── FactorAttributionList.tsx
│   │   ├── RecommendationList.tsx
│   │   ├── WhatIfSimulator.tsx
│   │   ├── InterventionModal.tsx
│   │   ├── OutcomeModal.tsx
│   │   ├── TimelineChart.tsx
│   │   └── EthicsBanner.tsx
│   └── pages/
│       ├── LoginPage.tsx
│       ├── WelfareDashboardPage.tsx
│       ├── PersonnelDetailPage.tsx
│       ├── CommanderDashboardPage.tsx
│       ├── AnalystDashboardPage.tsx
│       ├── PersonnelPortalPage.tsx
│       └── AdminAuditPage.tsx
```

---

## 6. Execution Plan

1. **Initialize Frontend Project**: Setup Vite + React + TS + Tailwind in `frontend/`.
2. **Implement Typed API Client & Types**: Model backend schemas exactly.
3. **Build Authentication & RBAC Layer**: AuthContext with token persistence and role guards.
4. **Build Core Reusable Components**: PriorityBadge, ScoreMeter, BaselineComparisonCard, TimelineChart, WhatIfSimulator, Modals.
5. **Implement All Role Dashboards**: Welfare Officer, Commander, Personnel, Analyst, Admin.
6. **Integrate End-to-End**: Verify API requests, mock fallback safety, live prediction and simulation runs.
7. **End-to-End Testing**: Execute full browser and test verification.
8. **Final Reporting & Documentation**: Produce `reports/frontend_completion_report.md`, `reports/demo_scenario.md`, and `reports/integration_test_report.md`.
