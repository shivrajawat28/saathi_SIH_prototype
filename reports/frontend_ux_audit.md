# SAATHI — Frontend UX, Accessibility & Cross-Role Audit Report

**Smart India Hackathon (SIH) Problem Statement 26186**  
**Title:** AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**Organization:** Ministry of Home Affairs | CRPF, Police II Division  
**System:** SAATHI  
**Date:** September 2026  
**Status:** **AUDITED & VERIFIED**  

---

## 1. Cross-Role User Experience Review

### 1.1 Welfare Officer Interface (`/welfare`, `/personnel/:id`)
* **Visual Hierarchy:** Clean dark slate theme with high contrast (`slate-950` background, `slate-900` cards, luminous color badges).
* **Batch Triage Table:** Real-time search, priority tier dropdown filters, sortable columns.
* **Personnel Detail Centerpiece:**
  - Continuous circular score meter with dynamic gradient rings (Green -> Amber -> Orange -> Red).
  - 12-month sequential composed chart (Duty Hours vs Rest Hours with interactive tooltips).
  - Baseline comparison card highlighting percentage shifts against personal historical norms.
  - Transparent factor attribution progress bars answering *"Why Did This Score Change?"*.
  - Rule-based welfare recommendations with one-click modal action triggers.
  - Interactive What-If Simulator with live score delta projection.
  - Human intervention history and follow-up outcome evaluations.

### 1.2 Commander Dashboard (`/commander`)
* **Aggregate Readiness Overview:** Unit-level percentage distributions across GREEN/YELLOW/ORANGE/RED.
* **Department Breakdown:** Stacked operational strain by department.
* **Privacy Isolation:** Strictly excludes private subjective survey text and individual check-in answers.

### 1.3 Personnel Self-Service Portal (`/portal`)
* **Personal Duty & Recovery Calendar:** Confidential view of personal operational hours.
* **Voluntary Check-in:** 1–5 scale check-in form with clear privacy notice (*"Voluntary input for welfare planning; not a medical diagnosis"*).

### 1.4 Admin Audit Portal (`/admin`)
* **Audit Trail Log Viewer:** Chronological immutable logs with search and status badges.
* **User Provisioning:** Modal to register new users with RBAC role assignments.

---

## 2. Accessibility & Standards Compliance

* **Semantic Structure:** Single `<h1>` per page, semantic `<header>`, `<main>`, `<nav>`, `<section>` elements.
* **Accessible Badges:** Priority tiers include both color indicators and text labels (e.g. `RED — Priority Review`, `GREEN — Stable Rhythm`).
* **Contrast & Legibility:** Minimum 4.5:1 text-to-background contrast ratio across all text elements.
* **Form Controls:** All `<input>` elements paired with explicit `id` and `<label htmlFor>` attributes.

---

## 3. Resilience & Error Handling

* **Token Expiration (401):** Interceptor automatically clears local storage and redirects to `/login`.
* **API Offline / Error States:** Components display graceful fallback cards (*"Unable to retrieve records. Please verify backend service connection."*) rather than failing silently or inventing mock numbers.
* **Data Completeness Gate:** If data is insufficient ($C < 0.35$), `ScoreMeter` renders an `INSUFFICIENT DATA` card with explanation.
