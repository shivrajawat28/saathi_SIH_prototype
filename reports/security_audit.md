# SAATHI — Security, Secrets & Privacy Audit Report

**Smart India Hackathon (SIH) Problem Statement 26186**  
**Title:** AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**Organization:** Ministry of Home Affairs | CRPF, Police II Division  
**System:** SAATHI  
**Date:** September 2026  
**Status:** **AUDITED & HARDENED**  

---

## 1. Secrets & Credentials Audit

* **Repository Scan:** Regex pattern scan for hardcoded API keys, private RSA/ECDSA keys, AWS secrets, and plaintext passwords executed across all subdirectories.
* **Findings:**
  - Zero live production secrets or private keys found in codebase.
  - `.env` is safely ignored in `.gitignore`.
  - `.env.example` contains documented placeholder parameters.
  - Default development `SECRET_KEY` in `backend/app/core/config.py` defaults to a development secret and is overridden by `os.environ["SECRET_KEY"]` in staging/production.
  - Demo accounts (`admin123`, `welfare123`, `commander123`, `analyst123`, `personnel123`) are explicitly flagged as prototype presets.

---

## 2. Privacy by Design & Psychological Safety

* **Pseudonymous Identifiers:** Personnel telemetry and HR records use pseudonymous keys (`P-000001` through `P-001470`). Real-world names, Aadhaar numbers, and phone numbers are completely absent.
* **Subjective Survey Isolation:**
  - Voluntary wellness check-in answers (`sleep_quality`, `fatigue_level`, `work_stress`, `mood_wellbeing`, `recovery_quality`, `self_reported_strain`) are strictly confined to authorized welfare decision support.
  - Command personnel receive aggregate unit welfare distributions (`/analytics/commander-overview`) and are barred from accessing individual check-in telemetry or subjective text.
* **Non-Surveillance Verification:**
  - Confirmed zero implementation of camera surveillance, facial emotion recognition, microphone feeds, voice stress analysis, WhatsApp inspection, keystroke logging, or continuous GPS tracking.
  - Telemetry is limited to objective operational logs (duty hours, shift patterns, leave history, deployment categories) and confidential voluntary self-reported check-ins.

---

## 3. JWT & Session Security

* **Algorithm:** HMAC-SHA256 (`HS256`).
* **Expiration:** 8-hour access token lifespan (`ACCESS_TOKEN_EXPIRE_MINUTES = 480`).
* **Token Validation:** Every protected route resolves current user from database via `get_current_user` dependency, ensuring revoked/deactivated accounts cannot authenticate with valid tokens.
* **CORS Policy:** Updated `BACKEND_CORS_ORIGINS` to allow explicit local ports (`http://localhost:3000`, `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:8000`), preventing arbitrary origin reflection.

---

## 4. Immutable Audit Trail

* **Logging Mechanism:** All state-modifying actions (`LOGIN`, `RUN_PREDICTION`, `RUN_WHATIF_SIMULATION`, `RECORD_INTERVENTION`, `RECORD_OUTCOME`, `CREATE_USER`, `SUBMIT_VOLUNTARY_WELLNESS`) invoke `AuditService.log_action()`.
* **Stored Attributes:** `timestamp` (UTC), `actor_id`, `actor_username`, `actor_role`, `action`, `target_resource`, `status`, `details`, and `ip_address`.
* **Access Control:** `GET /api/v1/audit/logs` is strictly restricted to `ADMIN` role. All other roles receive `403 Forbidden`.
