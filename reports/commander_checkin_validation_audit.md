# SAATHI — Commander Monthly Check-In Follow-Up & Server-Side Validation Hardening Audit Report

**Date:** 11 September 2026  
**System:** SAATHI (SIH 26186 — AI-Based Predictive Personnel Stress & Welfare Monitoring System for Uniformed Forces)  
**Organization:** Ministry of Home Affairs / Police II Division / CRPF  
**Scope:** Commander Monthly Check-In Follow-Up Feature Implementation & Backend Comprehensive Server-Side Validation Hardening  

---

## 1. Executive Summary

A targeted operational follow-up capability has been added to SAATHI, empowering Unit Commanders to track personnel participation in the monthly welfare check-in cycle and initiate administrative follow-up reminders. In strict adherence to ethical and psychological privacy standards, this feature **strictly separates administrative participation tracking from individual welfare analysis**.

Concurrently, the entire backend was audited and hardened with comprehensive server-side input validation, strict Pydantic v2 schemas, bounds checking, enum allowlists, pagination guards, IDOR protection, and rate limiting.

---

## 2. Feature Implementation: Commander Monthly Check-In Follow-Up

### Core Objectives
1. **Participation Visibility Without Surveillance:** Enable Unit Commanders to identify personnel whose expected monthly check-in window has elapsed without exposing confidential wellness signals, Support Scores, risk tiers, or survey content.
2. **Deterministic Monthly Calendar Cycle Rule:** The backend deterministically computes pending check-in status based on calendar cycles (`YYYY-MM`) and standard 30-day windows.
3. **Closed-Loop Follow-up Workflow:**
   - Commander views pending personnel in the operational unit.
   - Commander triggers an administrative check-in reminder (`POST /api/v1/commander/pending-checkins/{personnel_id}/follow-up`).
   - Action is immutably recorded in the central audit log (`AuditLog`).
   - Personnel receives a non-punitive reminder in the Personal Welfare Portal (`GET /api/v1/wellness/check-in-status`).
   - When personnel completes either the voluntary monthly check-in form or AI Companion session, the follow-up automatically transitions to `COMPLETED` and the personnel is cleared from the pending list.

### Non-Punitive Terminology & Ethical Framing
In accordance with ethical design requirements, no punitive terminology is used:
- ✅ *"Monthly Check-In Pending"* (Replaced: *"Non-compliant"*)
- ✅ *"Follow-up Required"* (Replaced: *"Problem personnel"*)
- ✅ *"Check-In Not Submitted"* (Replaced: *"Delinquent"*)
- ✅ *"Follow-up Requested"* (Replaced: *"Disciplinary flag"*)

---

## 3. Dedicated API Endpoints

| Method | Endpoint | Authorized Roles | Description | Privacy Restriction |
|---|---|---|---|---|
| `GET` | `/api/v1/commander/pending-checkins` | `COMMANDER`, `ADMIN`, `WELFARE_OFFICER` | Lists personnel with pending monthly check-ins for the active cycle. | Strictly excludes `support_score`, `priority`, `shap`, `fatigue`, `sleep`, `conversations`. |
| `GET` | `/api/v1/commander/pending-checkins/{personnel_id}` | `COMMANDER`, `ADMIN`, `WELFARE_OFFICER` | Detailed administrative view for a single pending personnel. | Withholds all subjective survey and AI companion notes. |
| `POST` | `/api/v1/commander/pending-checkins/{personnel_id}/follow-up` | `COMMANDER`, `ADMIN` | Initiates an administrative reminder action. | Creates immutable audit record. |
| `GET` | `/api/v1/wellness/check-in-status` | `PERSONNEL`, `ADMIN` | Checks current month submission status & active reminders. | Strictly scoped to authenticated personnel. |

---

## 4. Strict Privacy & RBAC Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SAATHI PRIVACY BARRIER                             │
├──────────────────────────────────────┬──────────────────────────────────────┤
│    COMMANDER ROLE ACCESS (ADMIN)     │   WELFARE OFFICER ACCESS (CLINICAL)  │
├──────────────────────────────────────┼──────────────────────────────────────┤
│  ✓ Personnel ID & Display Name       │  ✓ Continuous Support Score (0-100)  │
│  ✓ Assigned Unit / Division          │  ✓ Priority Risk Tiers (GREEN/RED)   │
│  ✓ Operational Role                  │  ✓ SHAP Causal Feature Attribution   │
│  ✓ Last Check-In Date                │  ✓ Baseline Drift / Counterfactuals  │
│  ✓ Expected Check-In Month           │  ✓ Voluntary AI Companion Summaries  │
│  ✓ Days Overdue (Window elapsed)     │  ✓ Confidential Survey Responses     │
│  ✓ Follow-up Status                  │  ✓ Welfare Recommendations & Actions │
│                                      │                                      │
│  ❌ NO Support Scores                │                                      │
│  ❌ NO Risk Categorizations          │                                      │
│  ❌ NO Survey Text or Answers        │                                      │
│  ❌ NO Chatbot Conversations         │                                      │
│  ❌ NO SHAP Explanations             │                                      │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 5. Server-Side Validation Hardening Matrix

| Component / Layer | Hardening Measure | Enforced Constraints | Error Code |
|---|---|---|---|
| **Pydantic Schemas** | Strict Field validation | Minimum/maximum lengths, non-empty strings, whitespace trimming. | `HTTP 422` |
| **Numeric Inputs** | Range & finiteness validation | `sleep_quality` (1.0–5.0), `fatigue_level` (1.0–5.0), non-negative duty/workload hours. | `HTTP 422` |
| **Enums** | Strict allowlists | `role` in `{"ADMIN", "WELFARE_OFFICER", "COMMANDER", "ANALYST", "PERSONNEL"}`, `status` in `{"PENDING", "OVERDUE", "FOLLOW_UP_REQUESTED", "COMPLETED"}`. | `HTTP 422` |
| **Pagination** | Bounds checking | `limit` (1..100), `offset` (>=0). Reject abusive unbounded queries. | `HTTP 422` |
| **Payload Limits** | String length restrictions | Notes max 256 chars, chat messages max 1000 chars, conversation batches max 50 items. | `HTTP 422` |
| **IDOR Protection** | Server-side identity derivation | Personnel can only access their own profile/conversation. Commanders cannot spoof `unit_id` query params. | `HTTP 403` |
| **SQL Injection** | SQLAlchemy ORM parameterized queries | Zero string concatenation in query construction. | N/A |

---

## 6. Fresh Test Verification Results

### Backend & ML Pytest Suite
```bash
pytest backend/tests/ tests/ -vv
```
**Results:** `64 passed in 3.06s` (100% pass rate)

Key Test Cases:
- `test_commander_can_get_pending_checkins`: PASSED
- `test_commander_pending_checkins_privacy_boundary`: PASSED
- `test_unauthorized_roles_blocked_from_commander_pending_checkins`: PASSED
- `test_commander_can_view_personnel_followup_detail`: PASSED
- `test_commander_request_followup_workflow`: PASSED
- `test_commander_request_followup_nonexistent_personnel`: PASSED
- `test_server_side_validation_hardening`: PASSED
- `test_companion_consent_required`: PASSED
- `test_companion_rbac_commander_and_analyst_blocked`: PASSED

### Frontend Vitest Suite
```bash
npm --prefix frontend test -- --run
```
**Results:** `7 test files passed, 22 tests passed in 1.78s`

### Frontend Production Build
```bash
npm --prefix frontend run build
```
**Results:** `✓ built in 1.61s` (0 TypeScript / CSS errors).

---

## 7. Files Changed / Added

1. `backend/app/models/follow_up.py` [NEW] — `CheckInFollowUp` database model.
2. `backend/app/models/__init__.py` [MODIFY] — Registered `CheckInFollowUp`.
3. `backend/app/schemas/commander.py` [NEW] — Pydantic schemas for pending check-in list, detail, and follow-up requests.
4. `backend/app/schemas/telemetry.py` [MODIFY] — Added `PersonnelCheckInStatusResponse` and validated survey bounds.
5. `backend/app/schemas/auth.py` [MODIFY] — Strict field validation and enum constraints on user creation.
6. `backend/app/schemas/intervention.py` [MODIFY] — Enforced strict bounds on intervention creation/outcome schemas.
7. `backend/app/services/commander_service.py` [NEW] — Implemented calendar-cycle logic, filtering, pagination, and follow-up persistence.
8. `backend/app/api/commander.py` [NEW] — Commander API router mounted at `/api/v1/commander`.
9. `backend/app/api/api_v1.py` [MODIFY] — Included `commander_router`.
10. `backend/app/api/wellness.py` [MODIFY] — Added `/check-in-status` endpoint and automated follow-up resolution on submission.
11. `frontend/src/types/index.ts` [MODIFY] — Added TypeScript interfaces for Commander follow-up and personnel check-in status.
12. `frontend/src/api/commander.ts` [NEW] — Commander API client methods.
13. `frontend/src/api/wellness.ts` [MODIFY] — Added `getCheckInStatus` method.
14. `frontend/src/pages/CommanderDashboardPage.tsx` [MODIFY] — Added Monthly Check-In Follow-up card, summary badges, filters, data table, and restricted modal.
15. `frontend/src/pages/PersonnelPortalPage.tsx` [MODIFY] — Added check-in status banner and reminder notification.
16. `backend/tests/test_commander_followup.py` [NEW] — Pytest test suite for Commander follow-up & validation hardening.
17. `frontend/src/tests/commander_followup.test.tsx` [NEW] — Vitest unit tests for Commander follow-up UI and privacy boundary.

---

## 8. Conclusion

The Commander Monthly Check-In Follow-Up capability is fully operational, privacy-hardened, and integrated with the institutional SAATHI design system. The system now provides complete operational visibility for unit leadership while preserving psychological safety and confidentiality for uniformed personnel.
