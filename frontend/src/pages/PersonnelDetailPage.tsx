import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  UserCheck,
  Building,
  Briefcase,
  Calendar,
  History,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  PlusCircle,
  CheckCircle2,
  Compass,
  Tent,
  GraduationCap,
  BellRing
} from 'lucide-react';
import { ScoreMeter } from '../components/ScoreMeter';
import { TimelineChart } from '../components/TimelineChart';
import { BaselineComparisonCard } from '../components/BaselineComparisonCard';
import { FactorAttributionList } from '../components/FactorAttributionList';
import { RecommendationList } from '../components/RecommendationList';
import { WhatIfSimulator } from '../components/WhatIfSimulator';
import { InterventionModal } from '../components/InterventionModal';
import { OutcomeModal } from '../components/OutcomeModal';
import { PriorityBadge } from '../components/PriorityBadge';
import { VoluntaryConversationCard } from '../components/VoluntaryConversationCard';

import { personnelApi } from '../api/personnel';
import { predictionsApi } from '../api/predictions';
import { interventionsApi } from '../api/interventions';
import {
  HRProfile,
  PersonnelTimelineResponse,
  PredictionResponse,
  InterventionResponse,
  OutcomeResponse,
  WelfareRecommendation
} from '../types';

export const PersonnelDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const personnelId = id || 'P-000013';
  const navigate = useNavigate();

  const [hrProfile, setHrProfile] = useState<HRProfile | null>(null);
  const [timelineData, setTimelineData] = useState<PersonnelTimelineResponse | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [interventions, setInterventions] = useState<InterventionResponse[]>([]);

  const [selectedMonthIdx, setSelectedMonthIdx] = useState<number>(12);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [isInterventionModalOpen, setIsInterventionModalOpen] = useState<boolean>(false);
  const [selectedDefaultRecType, setSelectedDefaultRecType] = useState<string>('WORKLOAD_REVIEW');
  const [isOutcomeModalOpen, setIsOutcomeModalOpen] = useState<boolean>(false);
  const [activeInterventionIdForOutcome, setActiveInterventionIdForOutcome] = useState<string | null>(null);

  const loadAllPersonnelData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [profileRes, timelineRes, predictionRes, interventionsRes] = await Promise.all([
        personnelApi.getProfile(personnelId).catch(() => null),
        personnelApi.getTimeline(personnelId).catch(() => null),
        predictionsApi.predictPersonnel(personnelId).catch(() => null),
        interventionsApi.getInterventionsForPersonnel(personnelId).catch(() => [])
      ]);

      setHrProfile(profileRes);
      setTimelineData(timelineRes);
      setPrediction(predictionRes);
      setInterventions(interventionsRes);

      if (timelineRes && timelineRes.timeline.length > 0) {
        setSelectedMonthIdx(timelineRes.timeline[timelineRes.timeline.length - 1].month_idx);
      }
    } catch (err: any) {
      console.error('Failed to load personnel data:', err);
      setError('Failed to retrieve personnel records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllPersonnelData();
  }, [personnelId]);

  const currentTimelineRecord = timelineData?.timeline.find(
    (item) => item.month_idx === selectedMonthIdx
  ) || (timelineData?.timeline ? timelineData.timeline[timelineData.timeline.length - 1] : undefined);

  const deployedMonthsCount = timelineData?.timeline.filter((item) => item.is_deployed).length ?? 0;

  const handleOpenIntervention = (rec?: WelfareRecommendation) => {
    if (rec) {
      setSelectedDefaultRecType(rec.type);
    } else {
      setSelectedDefaultRecType('WORKLOAD_REVIEW');
    }
    setIsInterventionModalOpen(true);
  };

  const handleOpenOutcome = (interventionId: string) => {
    setActiveInterventionIdForOutcome(interventionId);
    setIsOutcomeModalOpen(true);
  };

  const handleInterventionCreated = (newIntervention: InterventionResponse) => {
    setInterventions([newIntervention, ...interventions]);
  };

  const handleOutcomeRecorded = (newOutcome: OutcomeResponse) => {
    setInterventions(
      interventions.map((item) => {
        if (item.intervention_id === newOutcome.intervention_id) {
          return {
            ...item,
            status: newOutcome.outcome_status === 'IMPROVED' ? 'RESOLVED' : 'FOLLOW_UP_REQUIRED',
            outcomes: [newOutcome, ...item.outcomes]
          };
        }
        return item;
      })
    );
  };

  if (loading) {
    return (
      <div className="p-12 flex flex-col items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 text-saathi-primary animate-spin mb-3" />
        <span className="text-xs text-saathi-textMuted">Loading personnel telemetry and predictive baseline...</span>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 space-y-5 max-w-7xl mx-auto">
      
      {/* Top Navigation & Profile Header */}
      <div className="bg-white border border-saathi-border p-4 sm:p-5 rounded-lg shadow-gov flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded bg-saathi-bg hover:bg-saathi-primarySubtle border border-saathi-border text-saathi-textDark transition-colors"
            title="Back to Triage"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>

          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl sm:text-2xl font-black text-saathi-textDark font-mono">{personnelId}</h1>
              <span className="text-xs font-bold text-saathi-textMuted">
                {hrProfile?.job_role || 'Field Operations'}
              </span>
              <PriorityBadge priority={prediction?.priority || 'GREEN'} size="sm" />
            </div>

            <div className="flex flex-wrap items-center gap-3 text-xs text-saathi-textMuted mt-1">
              <span className="flex items-center gap-1 font-medium">
                <Building className="w-3.5 h-3.5 text-saathi-primary" />
                {hrProfile?.department || 'Operations'}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1 font-medium">
                <Briefcase className="w-3.5 h-3.5 text-saathi-primary" />
                Level {hrProfile?.job_level ?? 2} ({hrProfile?.years_in_service ?? 5} yrs in service)
              </span>
              <span>•</span>
              <span className="flex items-center gap-1 font-mono font-bold text-saathi-primary">
                Assessment Period: Month {selectedMonthIdx}
              </span>
            </div>
          </div>
        </div>

        {/* Action button to record human intervention */}
        <div className="flex items-center gap-3 self-start md:self-auto">
          <button
            onClick={() => handleOpenIntervention()}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded bg-saathi-saffron hover:bg-saathi-saffronHover text-white font-bold text-xs shadow-xs transition-colors cursor-pointer uppercase tracking-wider"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Record Welfare Action</span>
          </button>
        </div>
      </div>

      {/* 1. Score Meter & High-Level Support Indicators */}
      <ScoreMeter
        score={prediction?.support_score ?? 20.0}
        priority={prediction?.priority ?? 'GREEN'}
        reliability={prediction?.prediction_reliability ?? 0.85}
        completeness={prediction?.data_completeness ?? 1.0}
        baselineMaturityMonths={prediction?.baseline_maturity_months ?? 8}
        humanReviewRequired={prediction?.human_review_required ?? false}
      />

      {/* Operational & Deployment Context Card (SIH PS 26186 Indicators) */}
      <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
        <div className="flex items-center justify-between mb-3 border-b border-saathi-border pb-2.5">
          <div>
            <h3 className="text-base font-bold text-saathi-textDark flex items-center gap-2">
              <Compass className="w-4 h-4 text-saathi-primary" />
              <span>Operational Deployment, Transfer & Readiness Context</span>
            </h3>
            <p className="text-xs text-saathi-textMuted mt-0.5">
              Service history, deployment intensity, and training commitments from administrative telemetry.
            </p>
          </div>
          <span className="text-[10px] font-mono font-bold text-saathi-textMuted bg-saathi-bg border border-saathi-border px-2 py-0.5 rounded">
            Synthetic Operational Record
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="p-3 rounded border border-saathi-border bg-saathi-bg">
            <div className="flex items-center gap-1.5 text-xs font-bold text-saathi-textMuted mb-1">
              <Tent className="w-3.5 h-3.5 text-amber-700" />
              <span>Deployment Status</span>
            </div>
            <div className="text-xs font-bold text-saathi-textDark mt-0.5">
              {currentTimelineRecord?.is_deployed ? 'Active Field Deployment' : 'Stationary Base Duty'}
            </div>
            <span className="text-[11px] text-amber-800 font-mono font-semibold">
              Intensity Level: {currentTimelineRecord?.operational_intensity ?? 1} / 5
            </span>
          </div>

          <div className="p-3 rounded border border-saathi-border bg-saathi-bg">
            <div className="flex items-center gap-1.5 text-xs font-bold text-saathi-textMuted mb-1">
              <Calendar className="w-3.5 h-3.5 text-saathi-primary" />
              <span>Cumulative Deployment</span>
            </div>
            <div className="text-xs font-bold text-saathi-textDark mt-0.5">
              {deployedMonthsCount} of 12 Months
            </div>
            <span className="text-[11px] text-saathi-textMuted font-mono">
              {((deployedMonthsCount / 12) * 100).toFixed(0)}% Field Exposure
            </span>
          </div>

          <div className="p-3 rounded border border-saathi-border bg-saathi-bg">
            <div className="flex items-center gap-1.5 text-xs font-bold text-saathi-textMuted mb-1">
              <History className="w-3.5 h-3.5 text-saathi-primary" />
              <span>Movement & Transfer</span>
            </div>
            <div className="text-xs font-bold text-saathi-textDark mt-0.5">
              {hrProfile?.years_in_current_role ? `${hrProfile.years_in_current_role} yrs in current post` : 'Moderate Rotation'}
            </div>
            <span className="text-[11px] text-saathi-textMuted font-mono">
              {hrProfile?.years_with_curr_supervisor ? `${hrProfile.years_with_curr_supervisor} yrs with supervisor` : 'Standard Rotation'}
            </span>
          </div>

          <div className="p-3 rounded border border-saathi-border bg-saathi-bg">
            <div className="flex items-center gap-1.5 text-xs font-bold text-saathi-textMuted mb-1">
              <GraduationCap className="w-3.5 h-3.5 text-emerald-700" />
              <span>Training & Readiness</span>
            </div>
            <div className="text-xs font-bold text-saathi-textDark mt-0.5">
              {hrProfile?.training_times_last_year ?? 2} Modules Completed
            </div>
            <span className="text-[11px] text-emerald-700 font-mono font-semibold">
              Regular Annual Cadence
            </span>
          </div>
        </div>

        {/* Proactive Alert Notice */}
        {prediction?.priority === 'RED' && (
          <div className="mt-3.5 p-3 rounded border border-red-300 bg-red-50/70 flex items-start gap-2.5">
            <BellRing className="w-4 h-4 text-red-700 shrink-0 mt-0.5" />
            <div>
              <div className="text-xs font-bold text-red-900">
                Automated Welfare Priority Alert: Emerging Strain Pattern Detected
              </div>
              <p className="text-[11px] text-red-800 mt-0.5 leading-relaxed">
                Elevated duty hours ({currentTimelineRecord?.duty_hours.toFixed(1)} hrs, +{currentTimelineRecord?.duty_pct_change?.toFixed(1)}% vs baseline), night shift surge ({currentTimelineRecord?.night_shifts} shifts), and prolonged leave gap ({currentTimelineRecord?.days_since_prev_leave} days). Authorized human review recommended.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* 2. 12-Month Interactive Longitudinal Timeline */}
      {timelineData && (
        <TimelineChart
          timeline={timelineData.timeline}
          selectedMonthIdx={selectedMonthIdx}
          onSelectMonth={(m) => setSelectedMonthIdx(m)}
        />
      )}

      {/* 3. Personal Baseline Comparison Grid */}
      <BaselineComparisonCard currentRecord={currentTimelineRecord} />

      {/* 4. Voluntary Wellness Conversation Signals (Non-Clinical Decision Support) */}
      <VoluntaryConversationCard
        personnelId={personnelId}
        onTakeAction={() => handleOpenIntervention()}
      />

      {/* 5. Explainability & Deterministic Recommendations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <FactorAttributionList factors={prediction?.top_factors || []} />
        <RecommendationList
          recommendations={prediction?.recommendations || []}
          onTakeAction={handleOpenIntervention}
        />
      </div>

      {/* 6. What-If Welfare Simulator */}
      <WhatIfSimulator
        personnelId={personnelId}
        currentScore={prediction?.support_score ?? 25.0}
        currentPriority={prediction?.priority ?? 'GREEN'}
      />

      {/* 7. Closed-Loop Welfare Interventions & Outcomes History */}
      <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
        <div className="flex items-center justify-between mb-3 border-b border-saathi-border pb-2.5">
          <div>
            <h3 className="text-base font-bold text-saathi-textDark">Closed-Loop Welfare Intervention History</h3>
            <p className="text-xs text-saathi-textMuted mt-0.5">
              Logged human officer actions, rest authorizations, and longitudinal follow-up outcome evaluations.
            </p>
          </div>
          <span className="text-[10px] font-mono font-bold text-saathi-textMuted bg-saathi-bg border border-saathi-border px-2 py-0.5 rounded">
            {interventions.length} Recorded
          </span>
        </div>

        {interventions.length === 0 ? (
          <div className="p-6 rounded border border-saathi-border bg-saathi-bg text-center text-saathi-textMuted text-xs">
            No historical interventions logged for this personnel. Use <strong>Record Welfare Action</strong> above to initiate proactive support.
          </div>
        ) : (
          <div className="space-y-3 mt-3">
            {interventions.map((item) => (
              <div
                key={item.intervention_id}
                className="p-3.5 rounded border border-saathi-border bg-saathi-bg space-y-2.5"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-saathi-textDark">
                      {item.intervention_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[11px] font-mono text-saathi-textMuted">({item.intervention_id})</span>
                  </div>

                  <div className="flex items-center gap-2.5">
                    <span className="text-xs text-saathi-textMuted">Date: {item.intervention_date}</span>
                    <span className={`text-[10px] uppercase font-bold px-2 py-0.2 rounded border ${
                      item.status === 'RESOLVED'
                        ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                        : 'bg-saathi-primarySubtle text-saathi-primary border-saathi-secondaryLight'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-saathi-textDark bg-white p-2.5 rounded border border-saathi-border font-medium">
                  {item.action_summary}
                </p>

                {/* Follow-up Outcomes */}
                {item.outcomes && item.outcomes.length > 0 ? (
                  <div className="pl-3 border-l-2 border-emerald-600 space-y-1 mt-1.5">
                    <span className="text-[11px] font-bold text-emerald-800 block">
                      Follow-up Outcome Recorded ({item.outcomes[0].review_date}):
                    </span>
                    <div className="text-xs text-saathi-textMuted">
                      Status: <strong className="text-emerald-800">{item.outcomes[0].outcome_status}</strong> — {item.outcomes[0].follow_up_notes}
                    </div>
                  </div>
                ) : (
                  <div className="flex justify-end pt-1">
                    <button
                      onClick={() => handleOpenOutcome(item.intervention_id)}
                      className="text-xs font-bold text-emerald-800 hover:text-emerald-900 border border-emerald-300 bg-emerald-50 px-3 py-1 rounded transition-colors"
                    >
                      Record Follow-up Outcome
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      <InterventionModal
        isOpen={isInterventionModalOpen}
        onClose={() => setIsInterventionModalOpen(false)}
        personnelId={personnelId}
        defaultType={selectedDefaultRecType}
        onInterventionCreated={handleInterventionCreated}
      />

      {activeInterventionIdForOutcome && (
        <OutcomeModal
          isOpen={isOutcomeModalOpen}
          onClose={() => setIsOutcomeModalOpen(false)}
          interventionId={activeInterventionIdForOutcome}
          onOutcomeRecorded={handleOutcomeRecorded}
        />
      )}

    </div>
  );
};
