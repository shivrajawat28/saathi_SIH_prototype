# SAATHI Database Schema & Entity-Relationship Model

## 1. Relational Entity Specifications

The database schema is implemented in SQLAlchemy 2.x and normalized to support longitudinal occupational telemetry, decision-support predictions, explanations, interventions, outcomes, and audit logs.

---

### Entity: `users`
Represents authenticated system users (administrators, welfare officers, commanders, analysts, personnel).
- `id`: `Integer` (Primary Key, Auto-increment)
- `username`: `String(64)` (Unique, Indexed)
- `email`: `String(128)` (Unique, Indexed)
- `hashed_password`: `String(255)` (Bcrypt hashed)
- `full_name`: `String(128)`
- `is_active`: `Boolean` (Default: `True`)
- `personnel_id`: `String(32)` (Foreign Key to `personnel.personnel_id`, Nullable)
- `created_at`: `DateTime` (UTC)
- `updated_at`: `DateTime` (UTC)

### Entity: `roles`
System access roles with explicit permission scopes.
- `id`: `Integer` (Primary Key)
- `name`: `String(32)` (`ADMIN`, `WELFARE_OFFICER`, `COMMANDER`, `ANALYST`, `PERSONNEL`)
- `description`: `String(255)`

### Entity: `user_roles`
Many-to-many relationship mapping users to roles.
- `user_id`: `Integer` (Foreign Key to `users.id`)
- `role_id`: `Integer` (Foreign Key to `roles.id`)

---

### Entity: `personnel`
Master pseudonymous registry of uniformed personnel.
- `personnel_id`: `String(32)` (Primary Key, e.g., `P-000001`, Indexed)
- `original_ref_id`: `String(64)` (Pseudonymized reference)
- `created_at`: `DateTime`
- `updated_at`: `DateTime`

### Entity: `hr_profiles`
Normalized static organizational attributes for each personnel.
- `id`: `Integer` (Primary Key)
- `personnel_id`: `String(32)` (Foreign Key to `personnel.personnel_id`, Unique, Indexed)
- `age`: `Integer`
- `gender`: `String(16)`
- `department`: `String(64)`
- `job_role`: `String(64)`
- `job_level`: `Integer` (1–5)
- `education_level`: `Integer` (1–5)
- `education_field`: `String(64)`
- `marital_status`: `String(32)`
- `distance_from_home`: `Integer` (km)
- `business_travel`: `String(32)`
- `overtime_eligible`: `String(8)` (`Yes`/`No`)
- `total_working_years`: `Integer`
- `years_in_service`: `Integer`
- `years_in_current_role`: `Integer`
- `years_since_last_promotion`: `Integer`
- `years_with_curr_supervisor`: `Float`
- `baseline_env_satisfaction`: `Integer` (1–4)
- `baseline_job_satisfaction`: `Integer` (1–4)
- `baseline_job_involvement`: `Integer` (1–4)
- `baseline_work_life_balance`: `Integer` (1–4)
- `baseline_rel_satisfaction`: `Integer` (1–4)
- `performance_rating`: `Integer` (1–4)
- `training_times_last_year`: `Integer`
- `monthly_income`: `Integer`

---

### Entity: `deployment_records`
Longitudinal operational deployment entries.
- `id`: `Integer` (Primary Key)
- `deployment_id`: `String(32)` (Unique, Indexed)
- `personnel_id`: `String(32)` (Foreign Key to `personnel.personnel_id`, Indexed)
- `month_idx`: `Integer` (1–12)
- `date`: `Date`
- `start_date`: `Date`
- `end_date`: `Date`
- `deployment_duration_days`: `Integer`
- `deployment_type`: `String(32)` (`Routine`, `Extended`, `High Tempo`, `Training/Operational`)
- `operational_intensity`: `Integer` (1–5)
- `hardship_level`: `Integer` (1–5)
- `recovery_required`: `Boolean`
- `location_category`: `String(64)`

### Entity: `leave_records`
Longitudinal authorized leave history.
- `id`: `Integer` (Primary Key)
- `leave_id`: `String(32)` (Unique, Indexed)
- `personnel_id`: `String(32)` (Foreign Key to `personnel.personnel_id`, Indexed)
- `month_idx`: `Integer` (1–12)
- `date`: `Date`
- `leave_start_date`: `Date`
- `leave_end_date`: `Date`
- `duration_days`: `Integer`
- `leave_type`: `String(32)` (`Annual`, `Casual`, `Medical/Authorized`, `Recovery`, `Other Authorized`)
- `days_since_previous_leave`: `Integer`

### Entity: `workload_records`
Longitudinal monthly duty, shift, and rest metrics.
- `id`: `Integer` (Primary Key)
- `personnel_id`: `String(32)` (Foreign Key to `personnel.personnel_id`, Indexed)
- `month_idx`: `Integer` (1–12, Indexed)
- `date`: `Date`
- `duty_hours`: `Float`
- `overtime_hours`: `Float`
- `night_shifts`: `Integer`
- `consecutive_duty_days`: `Integer`
- `rest_hours`: `Float`
- `workload_score`: `Float` (0–100)
- `operational_intensity`: `Integer` (1–5)
- `schedule_irregularity`: `Float` (1–5)

### Entity: `wellness_records`
Longitudinal voluntary check-ins (bounded 1–5 scale).
- `id`: `Integer` (Primary Key)
- `personnel_id`: `String(32)` (Foreign Key to `personnel.personnel_id`, Indexed)
- `month_idx`: `Integer` (1–12, Indexed)
- `date`: `Date`
- `sleep_quality`: `Float` (1–5, Nullable)
- `fatigue_level`: `Float` (1–5, Nullable)
- `work_stress`: `Float` (1–5, Nullable)
- `mood_wellbeing`: `Float` (1–5, Nullable)
- `work_life_balance`: `Float` (1–5, Nullable)
- `job_satisfaction`: `Float` (1–5, Nullable)
- `recovery_quality`: `Float` (1–5, Nullable)
- `self_reported_strain`: `Float` (1–5, Nullable)
- `checkin_completion`: `Boolean`

### Entity: `behavioral_records`
Non-invasive organizational behavioral delta indicators.
- `id`: `Integer` (Primary Key)
- `personnel_id`: `String(32)` (Foreign Key to `personnel.personnel_id`, Indexed)
- `month_idx`: `Integer` (1–12, Indexed)
- `date`: `Date`
- `attendance_change`: `Float`
- `leave_frequency_change`: `Float`
- `workload_change`: `Float`
- `sleep_change`: `Float`
- `routine_deviation`: `Float` (0–1)
- `performance_change`: `Float`
- `schedule_change`: `Float`
- `recovery_change`: `Float`

---

### Entity: `predictions`
Persisted ML decision-support outputs.
- `id`: `Integer` (Primary Key)
- `prediction_id`: `String(64)` (Unique, Indexed)
- `personnel_id`: `String(32)` (Foreign Key to `personnel.personnel_id`, Indexed)
- `prediction_month_idx`: `Integer`
- `support_score`: `Float` (0–100)
- `support_priority`: `String(16)` (`GREEN`, `YELLOW`, `ORANGE`, `RED`, `INSUFFICIENT_DATA`)
- `high_risk_probability`: `Float` (0–1)
- `prediction_reliability`: `Float` (0–1)
- `data_completeness`: `Float` (0–1)
- `baseline_maturity_months`: `Integer`
- `operating_threshold`: `Float` (Default: `0.50`)
- `human_review_required`: `Boolean`
- `created_at`: `DateTime`

### Entity: `prediction_explanations`
Top localized factor contributions explaining why the support score was generated.
- `id`: `Integer` (Primary Key)
- `prediction_id`: `String(64)` (Foreign Key to `predictions.prediction_id`, Indexed)
- `factor_name`: `String(128)`
- `direction`: `String(16)` (`increase`, `decrease`)
- `contribution_score`: `Float`

### Entity: `welfare_recommendations`
Deterministic, non-punitive decision-support recommendations.
- `id`: `Integer` (Primary Key)
- `prediction_id`: `String(64)` (Foreign Key to `predictions.prediction_id`, Indexed)
- `recommendation_type`: `String(64)` (`WORKLOAD_REVIEW`, `RECOVERY_LEAVE`, `WELFARE_CHECK_IN`, `COUNSELLING_REFERRAL`, `SCHEDULE_ADJUSTMENT`, `FOLLOW_UP_ASSESSMENT`)
- `priority_level`: `String(16)` (`LOW`, `MEDIUM`, `HIGH`)
- `reason`: `Text`

---

### Entity: `interventions`
Welfare actions recorded by authorized officers.
- `id`: `Integer` (Primary Key)
- `intervention_id`: `String(64)` (Unique, Indexed)
- `personnel_id`: `String(32)` (Foreign Key to `personnel.personnel_id`, Indexed)
- `officer_user_id`: `Integer` (Foreign Key to `users.id`)
- `intervention_type`: `String(64)`
- `intervention_date`: `Date`
- `status`: `String(32)` (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `CLOSED`)
- `action_summary`: `Text`
- `created_at`: `DateTime`
- `updated_at`: `DateTime`

### Entity: `intervention_outcomes`
Outcome monitoring for closed-loop support tracking.
- `id`: `Integer` (Primary Key)
- `intervention_id`: `String(64)` (Foreign Key to `interventions.intervention_id`, Indexed)
- `review_date`: `Date`
- `outcome_status`: `String(32)` (`IMPROVED`, `UNCHANGED`, `ESCALATED`)
- `follow_up_notes`: `Text`
- `recorded_by_user_id`: `Integer` (Foreign Key to `users.id`)

---

### Entity: `audit_logs`
Immutable audit log tracking all sensitive access and actions.
- `id`: `Integer` (Primary Key)
- `user_id`: `Integer` (Foreign Key to `users.id`, Nullable)
- `username`: `String(64)`
- `user_role`: `String(32)`
- `action`: `String(64)` (e.g., `VIEW_PREDICTION`, `RECORD_INTERVENTION`)
- `target_resource`: `String(128)`
- `ip_address`: `String(64)`
- `status`: `String(16)` (`SUCCESS`, `FORBIDDEN`, `ERROR`)
- `details`: `Text` (Non-sensitive metadata)
- `timestamp`: `DateTime` (Indexed, UTC)
