# SAATHI: AI-Based Predictive Personnel Stress & Welfare Monitoring System.

[![Tests](https://img.shields.io/badge/pytest-56%20passed-brightgreen.svg)]()
[![Vitest](https://img.shields.io/badge/vitest-16%20passed-brightgreen.svg)]()
[![Model](https://img.shields.io/badge/model-Balanced%20Random%20Forest%20%2B%20Calibration-blue.svg)]()
[![Backend](https://img.shields.io/badge/backend-FastAPI%20%2B%20SQLAlchemy%202.x-009688.svg)]()
[![Companion](https://img.shields.io/badge/AI%20Companion-Voice%20%26%20Text-purple.svg)]()
[![Explainability](https://img.shields.io/badge/explainability-SHAP%20Attribution-orange.svg)]()
[![Compliance](https://img.shields.io/badge/ethical%20guardrails-Active-success.svg)]()

> **Smart India Hackathon (SIH) Problem Statement:** SIH 26186  
> **Title:** AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
> **Organization:** Ministry of Home Affairs  
> **Department:** Central Reserve Police Force (CRPF), Police II Division  

---

## 🏛️ Executive Product Thesis

**SAATHI** is a privacy-first, non-diagnostic occupational decision-support system designed to identify meaningful deteriorations in occupational workload, recovery rhythm, deployment exposure, and voluntary self-reported wellness for uniformed forces personnel.

> *"SAATHI detects meaningful deterioration from a person's normal operational and wellness pattern, explains the signals behind the change, and recommends appropriate welfare interventions while keeping humans in control."*

The system empowers authorized **Welfare Officers** to provide timely, non-punitive, supportive human outreach before strain compounds into severe burnout or crisis.

```
DATA (HR, Duty, Leave, Deployment, Voluntary Wellness)
   │
   ▼
[1] Personal Baseline Engine (Historical causal window t <= T-1)
   │
   ▼
[2] Change & Deviation Detection (Z-scores, surge %, leave gap, recovery deficit)
   │
   ▼
[3] Voluntary AI Wellness Companion (Speech-to-Text, Voice, Structured Non-Clinical Signals)
   │
   ▼
[4] Locked ML Inference (Balanced Random Forest + Platt Calibration, tau = 0.50)
   │
   ▼
[5] Calibrated Support Score (0–100 scale: GREEN / YELLOW / ORANGE / RED)
   │
   ▼
[6] Factor Attribution & Reliability (SHAP-aligned feature contributions & data completeness)
   │
   ▼
[7] Model-Based What-If Welfare Simulator (Scenario projection for workload/rest adjustments)
   │
   ▼
[8] Deterministic Welfare Recommendation Engine (Non-punitive support actions)
   │
   ▼
[9] Authorized Welfare Officer Human Review (Human-in-the-loop decision & outreach)
   │
   ▼
[10] Closed-Loop Intervention & Outcome Tracking (Longitudinal recovery evaluation)
```

---

## ⚠️ Critical Ethical, Privacy & Operational Guardrails

1. **STRICTLY NOT A MEDICAL DIAGNOSIS SYSTEM**:
   - SAATHI **never** outputs clinical labels such as *"Depressed"*, *"Mentally ill"*, *"Psychologically unfit"*, or *"Dangerous employee"*.
   - All outputs represent occupational review priorities:
     - 🟢 **GREEN**: Stable Rhythm (Normal occupational and recovery rhythm, $S < 30$)
     - 🟡 **YELLOW**: Early Strain Indicators (Minor workload surge or reduced recovery, $30 \le S < 55$)
     - 🟠 **ORANGE**: Persistent Elevated Strain (Sustained strain warranting welfare check-in, $55 \le S < 75$)
     - 🔴 **RED**: Priority Welfare Review (Multi-signal cumulative strain warranting proactive review, $S \ge 75$)
2. **VOLUNTARY PARTICIPATION & VOICE SAFETY**:
   - The **SAATHI Wellness Companion** is strictly voluntary. Personnel choose whether and what to share.
   - **No Voice Stress / Lie Detection:** Voice audio is transcribed into text. The system does **not** claim to diagnose mental health from acoustic pitch, tone, or speech pauses.
   - **Emergency Crisis Handling:** If explicit self-harm or acute danger is communicated, the system provides compassionate emergency guidance (KIRAN 1800-599-0019 / Base Medical Officer) and initiates a high-priority human welfare alert.
3. **ZERO SURVEILLANCE POLICY**:
   - Strictly excludes facial emotion recognition, private WhatsApp/message reading, keystroke logging, social media monitoring, continuous camera surveillance, background microphone monitoring, and GPS tracking.
4. **ROLE-BASED ACCESS CONTROL (RBAC)**:
   - **Welfare Officers:** Access individual profiles, predictions, explainability, voluntary companion summaries, and record interventions.
   - **Unit Commanders:** View strictly aggregated unit-level readiness and welfare statistics. Commanders **never** see individual survey responses, private companion text, or personal profiles.
   - **Analysts:** View strictly anonymized research trends without personnel enumeration.
   - **Personnel:** View their own telemetry, voluntary check-ins, and interact with the Wellness Companion.
5. **DATA INTEGRITY DISCLAIMER**:
   - The current prototype utilizes an anonymized benchmark HR dataset alongside privacy-preserving synthetic longitudinal datasets for operational, leave, deployment, and voluntary wellness signals. It does **not** represent confidential or official CRPF personnel records.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node v22)
- SQLite (built-in default) or PostgreSQL 15+

### 1. Backend Service Setup & Launch
```bash
# Optional: create virtualenv
python3 -m venv .venv && source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Start backend server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive FastAPI Swagger Documentation is available at:
👉 **`http://localhost:8000/docs`**

### 2. Frontend Web App Setup & Launch
```bash
cd frontend
npm install
npm run dev
```
The React Dark UI dashboard is live at:
👉 **`http://localhost:5173`**

---

## 🔑 Demo Accounts & Canonical Scenario

All accounts use the password: `AdminSecurePassword123!` (or the Quick-Select role buttons on the login screen):

| Role | Username | Purpose |
| :--- | :--- | :--- |
| **Welfare Officer** | `welfare_officer` | Full access to cohort triage, individual timeline, SHAP factors, What-If simulator, and conversation signals |
| **Unit Commander** | `commander` | High-level aggregated unit statistics and readiness metrics (zero private surveys visible) |
| **Personnel (Demo Candidate)** | `personnel_p13` | Personnel **P-000013** portal with interactive AI Wellness Companion (Voice/Text) |
| **Personnel (Baseline Reference)** | `officer_p1` | Personnel **P-000001** portal showing stable baseline state |
| **System Admin** | `admin` | System configuration, user provisioning, and immutable audit logs |
| **Welfare Analyst** | `analyst` | Workforce trends and calibrated model performance distribution |

### Canonical Demo Walkthrough: Personnel P-000013

1. **Emerging Strain Detection:**
   - In Month 12, P-000013 shows a workload surge: **261.2 duty hours** (+38.3% vs personal baseline), **14 night shifts**, **38.3 rest hours** (deficit), and a **302-day leave gap**.
   - Model-calibrated Support Score: **88.1 (RED - Priority Welfare Review)**.
2. **Voluntary Wellness Conversation:**
   - P-000013 uses the **SAATHI Wellness Companion** via voice/text: *"Mujhe pichhle kuch dino se continuous night shifts ki wajah se bahut thakaan ho rahi hai aur neend proper nahi aa rahi."*
   - Assistant non-clinically extracts structured signals (Fatigue: Elevated, Sleep: Elevated, Workload: Elevated, Confidence: 88%) and compares against previous baseline.
3. **Welfare Officer Drilldown & Explainability:**
   - Welfare Officer opens P-000013 profile and sees top contributing drivers: Prolonged Leave Gap, Night Shift Surge, Recovery Deficit, and Voluntary Strain Signals.
4. **What-If Welfare Simulator (Model-Based Scenario Simulation):**
   - Welfare Officer tests adjusting schedule: reducing duty by **-40h**, reducing night shifts by **-8**, and granting restorative leave.
   - Model projects live score reduction: **88.1 → 80.3 (RED/ORANGE transition)**.
5. **Closed-Loop Action & Outcome Tracking:**
   - Officer logs a **Rest & Recovery Leave** intervention.
   - Outcome is tracked longitudinally across subsequent cycles.

---

## 🧪 Verification & Test Suite

### Running Backend Unit & Security Tests
```bash
pytest backend/tests/
```
*Result: 46/46 passed (including RBAC, IDOR, crisis safety, conversation extraction, and what-if simulation).*

### Running ML Pipeline & Data Quality Tests
```bash
pytest tests/
```
*Result: 10/10 passed (personal baseline, zero temporal leakage, feature completeness).*

### Running Frontend Tests & Production Build
```bash
npm --prefix frontend test
npm --prefix frontend run build
```
*Result: 16/16 passed in Vitest; production bundle built cleanly.*
