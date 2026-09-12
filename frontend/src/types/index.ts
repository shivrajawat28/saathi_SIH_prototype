/**
 * SAATHI TypeScript Domain Interfaces & API Contracts
 */

export type UserRole = 'ADMIN' | 'WELFARE_OFFICER' | 'COMMANDER' | 'ANALYST' | 'PERSONNEL';

export type PriorityTier = 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED' | 'INSUFFICIENT_DATA';

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: UserRole;
  personnel_id?: string | null;
  is_active: boolean;
  permissions: string[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export interface PersonnelSummary {
  personnel_id: string;
  department?: string;
  job_role?: string;
  job_level?: number;
  years_in_service?: number;
  latest_priority?: PriorityTier;
  latest_support_score?: number;
}

export interface HRProfile {
  age?: number;
  gender?: string;
  department?: string;
  job_role?: string;
  job_level?: number;
  education_level?: number;
  education_field?: string;
  marital_status?: string;
  distance_from_home?: number;
  business_travel?: string;
  overtime_eligible?: string;
  total_working_years?: number;
  years_in_service?: number;
  years_in_current_role?: number;
  years_since_last_promotion?: number;
  years_with_curr_supervisor?: number;
  baseline_env_satisfaction?: number;
  baseline_job_satisfaction?: number;
  baseline_work_life_balance?: number;
  training_times_last_year?: number;
}

export interface TimelineItem {
  month_idx: number;
  date: string;
  duty_hours: number;
  duty_hours_baseline?: number;
  duty_pct_change?: number;
  night_shifts: number;
  night_shifts_baseline?: number;
  night_shifts_pct_change?: number;
  rest_hours: number;
  workload_score: number;
  is_deployed: boolean;
  deployment_type?: string;
  operational_intensity?: number;
  took_leave: boolean;
  leave_type?: string;
  days_since_prev_leave?: number;
  self_reported_strain?: number | null;
  sleep_quality?: number | null;
  support_score?: number;
  support_priority?: PriorityTier;
}

export interface PersonnelTimelineResponse {
  personnel_id: string;
  total_months: number;
  timeline: TimelineItem[];
}

export interface TopFactor {
  factor: string;
  direction: 'increase' | 'decrease';
  contribution: number;
}

export interface WelfareRecommendation {
  type: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  reason: string;
}

export interface PredictionResponse {
  personnel_id: string;
  status: 'VALID' | 'INSUFFICIENT_DATA' | 'ERROR';
  support_score: number | null;
  priority: PriorityTier;
  high_risk_probability: number | null;
  prediction_reliability: number;
  data_completeness: number;
  baseline_maturity_months: number;
  operating_threshold: number;
  top_factors: TopFactor[];
  recommendations: WelfareRecommendation[];
  human_review_required: boolean;
  message?: string | null;
  ethical_guardrail?: string;
}

export interface BatchTriageItem {
  personnel_id: string;
  department?: string;
  job_role?: string;
  support_score: number;
  priority: PriorityTier;
  high_risk_probability?: number;
  prediction_reliability: number;
  data_completeness: number;
  human_review_required: boolean;
  predicted_at?: string;
}

export interface InterventionCreate {
  personnel_id: string;
  intervention_type: string;
  action_summary: string;
  intervention_date?: string;
}

export interface OutcomeCreate {
  outcome_status: 'IMPROVED' | 'UNCHANGED' | 'ESCALATED';
  follow_up_notes: string;
  review_date?: string;
}

export interface OutcomeResponse {
  id: number;
  intervention_id: string;
  review_date: string;
  outcome_status: 'IMPROVED' | 'UNCHANGED' | 'ESCALATED';
  follow_up_notes: string;
  recorded_by_username?: string;
  created_at: string;
}

export interface InterventionResponse {
  intervention_id: string;
  personnel_id: string;
  officer_username?: string;
  intervention_type: string;
  intervention_date: string;
  status: string;
  action_summary: string;
  created_at: string;
  outcomes: OutcomeResponse[];
}

export interface SimulationRequest {
  reduce_night_shifts?: number;
  reduce_duty_hours?: number;
  grant_recovery_days?: number;
  reduce_overtime_hours?: number;
}

export interface SimulationFactorChange {
  factor: string;
  before: any;
  after: any;
}

export interface SimulationResponse {
  personnel_id: string;
  simulation_only: boolean;
  current_score: number;
  projected_score: number;
  current_priority: PriorityTier;
  projected_priority: PriorityTier;
  projected_delta: number;
  parameter_changes: SimulationFactorChange[];
  projected_recommendations: WelfareRecommendation[];
  disclaimer: string;
}

export interface PriorityDistributionItem {
  priority: PriorityTier;
  count: number;
  percentage: number;
}

export interface DepartmentWelfareSummary {
  department: string;
  total_personnel: number;
  green_count: number;
  yellow_count: number;
  orange_count: number;
  red_count: number;
  avg_support_score: number;
}

export interface CommanderOverviewResponse {
  total_strength: number;
  high_risk_total: number;
  priority_distribution: PriorityDistributionItem[];
  department_breakdown: DepartmentWelfareSummary[];
  interventions_active_count: number;
  interventions_improved_count: number;
  data_completeness_avg: number;
  disclaimer: string;
}

export interface WellnessCheckInRequest {
  sleep_quality?: number;
  fatigue_level?: number;
  work_stress?: number;
  mood_wellbeing?: number;
  work_life_balance?: number;
  job_satisfaction?: number;
  recovery_quality?: number;
  self_reported_strain?: number;
}

export interface AuditLogEntry {
  id: number;
  user_id?: number;
  username: string;
  user_role: string;
  action: string;
  target_resource: string;
  status: string;
  details?: string;
  ip_address?: string;
  timestamp: string;
}

export interface StructuredWellnessSignals {
  sleep_difficulty: string;
  fatigue: string;
  workload_pressure: string;
  emotional_exhaustion: string;
  recovery_difficulty: string;
  personal_concern: string;
  morale_concern: string;
  social_withdrawal: boolean;
  positive_resilience_indicators: string[];
  sentiment_valence: string;
  urgency_level: 'NORMAL' | 'MODERATE' | 'ELEVATED' | 'CRISIS';
  extraction_confidence: number;
  primary_strain_driver?: string;
}

export interface CompanionChatMessage {
  sender: 'USER' | 'ASSISTANT';
  text: string;
  timestamp?: string;
  is_voice?: boolean;
}

export interface CompanionChatRequest {
  message: string;
  input_mode?: 'TEXT' | 'VOICE' | 'VOICE_FALLBACK_TEXT';
  consent_given: boolean;
  conversation_history?: CompanionChatMessage[];
}

export interface CompanionChatResponse {
  reply: string;
  ai_summary: string;
  extracted_signals: StructuredWellnessSignals;
  is_crisis: boolean;
  urgency_level: 'NORMAL' | 'MODERATE' | 'ELEVATED' | 'CRISIS';
  confidence: number;
  change_vs_previous?: string;
  welfare_signal_impact?: string;
  saved_conversation_id?: string;
}

export interface CompanionSubmitRequest {
  consent_given: boolean;
  input_mode: string;
  messages: CompanionChatMessage[];
}

export interface CompanionConversationSummary {
  id: number;
  conversation_id: string;
  personnel_id: string;
  created_at: string;
  consent_given: boolean;
  input_mode: string;
  ai_summary: string;
  structured_signals: StructuredWellnessSignals;
  confidence: number;
  urgency_level: string;
  is_crisis: boolean;
  welfare_signal_impact?: string;
  change_vs_previous?: string;
  status: 'PENDING_REVIEW' | 'ACKNOWLEDGED' | 'INTERVENTION_CREATED' | 'RESOLVED';
  welfare_officer_notes?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  messages?: CompanionChatMessage[];
}

export interface CompanionReviewRequest {
  status: string;
  notes?: string;
}

export interface VoiceTranscribeResponse {
  transcript: string;
  input_mode: string;
  fallback_used: boolean;
  confidence: number;
  message: string;
}

export interface PendingCheckInItem {
  personnel_id: string;
  display_name: string;
  unit: string;
  role: string;
  last_checkin_date?: string | null;
  expected_checkin_month: string;
  days_overdue: number;
  submission_status: 'NOT_SUBMITTED' | 'PENDING' | 'SUBMITTED';
  follow_up_status: 'NONE' | 'REQUESTED' | 'ACKNOWLEDGED' | 'COMPLETED';
  last_followup_at?: string | null;
  last_followup_by?: string | null;
}

export interface PendingCheckInsSummary {
  total_pending: number;
  overdue_count: number;
  followed_up_count: number;
  cycle_month: string;
  cycle_label: string;
  items: PendingCheckInItem[];
  page: number;
  page_size: number;
  total_items: number;
}

export interface CheckInFollowUpRequest {
  notes?: string;
}

export interface CheckInFollowUpResponse {
  id: number;
  personnel_id: string;
  target_month: string;
  status: string;
  requested_by_username: string;
  requested_at: string;
  notes?: string | null;
  message: string;
}

export interface PersonnelCheckInStatusResponse {
  personnel_id: string;
  current_cycle_month: string;
  is_submitted: boolean;
  submission_status: string;
  last_checkin_date?: string | null;
  follow_up_requested: boolean;
  follow_up_status: string;
  last_followup_at?: string | null;
  message: string;
}
