# SAATHI — API Contract vs. Implementation Audit Report

**Smart India Hackathon (SIH) Problem Statement 26186**  
**Title:** AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**Organization:** Ministry of Home Affairs | CRPF, Police II Division  
**System:** SAATHI  
**Date:** September 2026  
**Status:** **AUDITED & FULLY SYNCHRONIZED**  

---

## 1. API Route & Contract Mapping

| Route Pattern | Method | Contract Schema | Backend Implementation | Frontend API Client | Match Status |
| :--- | :---: | :--- | :--- | :--- | :---: |
| `/api/v1/auth/login` | POST | `LoginRequest` -> `Token` | `auth.login` (`backend/app/api/auth.py`) | `authApi.login` | **SYNCED** |
| `/api/v1/auth/me` | GET | `None` -> `UserProfile` | `auth.get_current_user_profile` | `authApi.getProfile` | **SYNCED** |
| `/api/v1/auth/users` | POST | `UserCreate` -> `UserResponse` | `auth.create_user` | `authApi.createUser` | **SYNCED** |
| `/api/v1/personnel/` | GET | Query params -> `List[PersonnelSummary]` | `personnel.list_personnel` | `personnelApi.list` | **SYNCED** |
| `/api/v1/personnel/{id}` | GET | Path -> `HRProfileSchema` | `personnel.get_personnel_profile` | `personnelApi.getById` | **SYNCED** |
| `/api/v1/personnel/{id}/timeline` | GET | Path -> `PersonnelTimelineResponse` | `personnel.get_personnel_timeline` | `personnelApi.getTimeline` | **SYNCED** |
| `/api/v1/predictions/batch-triage` | GET | Query -> `List[BatchTriageItem]` | `predictions.get_batch_triage` | `predictionsApi.getBatchTriage` | **SYNCED** |
| `/api/v1/predictions/personnel/{id}` | POST | Path -> `PredictionResponse` | `predictions.generate_prediction_for_personnel` | `predictionsApi.generatePrediction` | **SYNCED** |
| `/api/v1/simulations/personnel/{id}` | POST | `SimulationRequest` -> `SimulationResponse` | `simulations.run_scenario_simulation` | `simulationsApi.runSimulation` | **SYNCED** |
| `/api/v1/interventions/` | POST | `InterventionCreate` -> `InterventionResponse` | `interventions.create_welfare_intervention` | `interventionsApi.create` | **SYNCED** |
| `/api/v1/interventions/personnel/{id}` | GET | Path -> `List[InterventionResponse]` | `interventions.get_personnel_interventions` | `interventionsApi.getForPersonnel` | **SYNCED** |
| `/api/v1/interventions/{id}/outcomes` | POST | `OutcomeCreate` -> `OutcomeResponse` | `interventions.record_intervention_outcome` | `interventionsApi.recordOutcome` | **SYNCED** |
| `/api/v1/analytics/commander-overview` | GET | `None` -> `CommanderAnalyticsResponse` | `analytics.get_commander_overview` | `analyticsApi.getCommanderOverview` | **SYNCED** |
| `/api/v1/wellness/check-in` | POST | `WellnessCheckInRequest` -> `WellnessCheckInResponse` | `wellness.submit_voluntary_check_in` | `wellnessApi.submitCheckIn` | **SYNCED** |
| `/api/v1/audit/logs` | GET | Query -> `List[AuditLogEntry]` | `audit.get_audit_logs` | `auditApi.getLogs` | **SYNCED** |

---

## 2. Request / Response Schema Validation

1. **Pydantic v2 Consistency:** All schemas in `backend/app/schemas/` utilize `model_validate` or direct instantiation compatible with Pydantic v2.
2. **Date & Timestamp Formats:** All dates are formatted as ISO-8601 strings (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`), parsing cleanly into JavaScript `Date` objects on the client.
3. **Simulation Factor Change Schema:** Both backend `SimulationFactorChange` and frontend `types/index.ts` represent `{ factor: string, before: any, after: any }`.
4. **Error Response Schema:** FastAPI standardized error payload `{"detail": "Error message"}` is caught by Axios interceptor and displayed cleanly in toast/card UI components.
