# SAATHI REST API Specification & Endpoint Contracts

## 1. Authentication & Identity Endpoints

### `POST /api/v1/auth/login`
Authenticates a user and returns a signed JWT access token.
- **Request Body**:
  ```json
  {
    "username": "welfare_officer_1",
    "password": "SecurePassword123!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 28800,
    "user": {
      "id": 2,
      "username": "welfare_officer_1",
      "email": "welfare.officer@forces.gov.in",
      "role": "WELFARE_OFFICER",
      "personnel_id": null
    }
  }
  ```

### `GET /api/v1/auth/me`
Fetches authenticated user profile and permissions.
- **Headers**: `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  {
    "id": 2,
    "username": "welfare_officer_1",
    "email": "welfare.officer@forces.gov.in",
    "role": "WELFARE_OFFICER",
    "permissions": ["VIEW_ASSIGNED_PERSONNEL", "VIEW_PREDICTIONS", "CREATE_INTERVENTION", "RECORD_OUTCOME"]
  }
  ```

---

## 2. Personnel & Telemetry Endpoints

### `GET /api/v1/personnel/`
Lists personnel assigned to the authorized officer. Supports filtering by department, job role, and search.
- **Query Params**: `limit=50&offset=0&department=Research+%26+Development`
- **Response (200 OK)**:
  ```json
  {
    "total": 1470,
    "items": [
      {
        "personnel_id": "P-000001",
        "age": 18,
        "department": "Research & Development",
        "job_role": "Laboratory Technician",
        "job_level": 1,
        "years_in_service": 0,
        "overtime_eligible": "No"
      }
    ]
  }
  ```

### `GET /api/v1/personnel/{personnel_id}/timeline`
Retrieves longitudinal operational telemetry and baseline stats for an individual.
- **Response (200 OK)**:
  ```json
  {
    "personnel_id": "P-000001",
    "months_count": 12,
    "timeline": [
      {
        "month_idx": 6,
        "date": "2025-06-01",
        "duty_hours": 181.6,
        "duty_hours_baseline": 187.8,
        "duty_pct_change": -3.3,
        "night_shifts": 2,
        "rest_hours": 94.2,
        "workload_score": 32.5,
        "is_deployed": false,
        "took_leave": true
      }
    ]
  }
  ```

---

## 3. Prediction & Explainability Endpoints

### `POST /api/v1/predictions/personnel/{personnel_id}`
Generates or retrieves the latest Welfare Support Priority prediction using the locked Random Forest + Calibration ML pipeline.
- **Headers**: `Authorization: Bearer <token>`
- **Query Params**: `operating_threshold=0.50` (Optional, default: 0.50)
- **Response (200 OK)**:
  ```json
  {
    "personnel_id": "P-000412",
    "support_score": 67.4,
    "priority": "ORANGE",
    "high_risk_probability": 0.674,
    "prediction_reliability": 0.81,
    "data_completeness": 0.92,
    "baseline_maturity_months": 8,
    "operating_threshold": 0.50,
    "top_factors": [
      {
        "factor": "Night shifts surge vs personal baseline",
        "direction": "increase",
        "contribution": 0.24
      },
      {
        "factor": "Consecutive duty days extension",
        "direction": "increase",
        "contribution": 0.19
      }
    ],
    "recommendations": [
      {
        "type": "WORKLOAD_REVIEW",
        "priority": "HIGH",
        "reason": "Operational duty hours and night shifts have escalated significantly above personal baseline."
      }
    ],
    "human_review_required": true,
    "ethical_guardrail": "Authorized decision support only. Identifies occupational welfare review priority; not a clinical assessment or punitive tool."
  }
  ```

### Cold-Start / Insufficient Data Response:
When `data_completeness < 0.35`:
```json
{
  "personnel_id": "P-000891",
  "status": "INSUFFICIENT_DATA",
  "support_priority": "INSUFFICIENT_DATA",
  "support_score": null,
  "high_risk_probability": null,
  "prediction_reliability": 0.0,
  "data_completeness": 0.25,
  "message": "Insufficient operational and voluntary wellness signals to establish a reliable welfare review.",
  "top_factors": [],
  "recommendations": [
    {
      "type": "WELFARE_CHECK_IN",
      "priority": "MEDIUM",
      "reason": "Telemetry signals are incomplete. An informal welfare check-in is recommended to verify operational status."
    }
  ]
}
```

---

## 4. Counterfactual "What-If" Scenario Simulator Contract

### `POST /api/v1/simulations/personnel/{personnel_id}`
Simulates the projected impact of operational schedule or leave adjustments on the welfare support score without modifying permanent records.
- **Request Body**:
  ```json
  {
    "reduce_night_shifts": 3,
    "reduce_duty_hours": 20,
    "grant_recovery_days": 5
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "personnel_id": "P-000412",
    "simulation_only": true,
    "current_score": 67.4,
    "projected_score": 38.1,
    "current_priority": "ORANGE",
    "projected_priority": "YELLOW",
    "projected_delta": -29.3,
    "parameter_changes": [
      {"factor": "night_shifts", "before": 8, "after": 5},
      {"factor": "duty_hours", "before": 235.0, "after": 215.0},
      {"factor": "recovery_days", "before": 0, "after": 5}
    ],
    "disclaimer": "Scenario projection only. Represents model estimation under simulated operational modifications, not a guaranteed outcome."
  }
  ```

---

## 5. Welfare Interventions & Outcome Tracking Endpoints

### `POST /api/v1/interventions/`
Records a human-initiated supportive welfare action.
- **Request Body**:
  ```json
  {
    "personnel_id": "P-000412",
    "intervention_type": "RECOVERY_LEAVE",
    "action_summary": "Authorized 5 days of recovery rest post high-intensity border outpost deployment.",
    "intervention_date": "2025-11-15"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "intervention_id": "INTV-20251115-00412",
    "personnel_id": "P-000412",
    "status": "IN_PROGRESS",
    "officer_name": "Major S. Sharma",
    "created_at": "2025-11-15T09:30:00Z"
  }
  ```

### `POST /api/v1/interventions/{intervention_id}/outcomes`
Records follow-up outcome tracking for a recorded intervention.
- **Request Body**:
  ```json
  {
    "outcome_status": "IMPROVED",
    "follow_up_notes": "Officer completed recovery rest. Subsequent duty cycle stable; sleep quality restored to baseline."
  }
  ```

---

## 6. Voluntary Wellness Survey Submission Endpoint

### `POST /api/v1/wellness/check-in`
Allows individual personnel to submit voluntary wellness indicators.
- **Request Body**:
  ```json
  {
    "sleep_quality": 4.0,
    "fatigue_level": 2.0,
    "work_stress": 2.0,
    "mood_wellbeing": 4.0,
    "work_life_balance": 4.0
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "SUCCESS",
    "message": "Voluntary check-in recorded successfully. Data is strictly confidential."
  }
  ```
