import React, { useState, useEffect } from 'react';
import {
  HeartHandshake,
  ShieldCheck,
  Lock,
  CheckCircle2,
  AlertCircle,
  Clock,
  Send,
  Sparkles,
  MessageSquare,
  FileSpreadsheet,
  Activity,
  Bell
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { wellnessApi } from '../api/wellness';
import { personnelApi } from '../api/personnel';
import { HRProfile, PersonnelTimelineResponse, PersonnelCheckInStatusResponse } from '../types';
import { WellnessCompanion } from '../components/WellnessCompanion';

export const PersonnelPortalPage: React.FC = () => {
  const { user } = useAuth();
  const personnelId = user?.personnel_id || 'P-000013';

  const [activeTab, setActiveTab] = useState<'companion' | 'survey' | 'telemetry'>('companion');
  const [hrProfile, setHrProfile] = useState<HRProfile | null>(null);
  const [timelineData, setTimelineData] = useState<PersonnelTimelineResponse | null>(null);
  const [checkInStatus, setCheckInStatus] = useState<PersonnelCheckInStatusResponse | null>(null);

  // Survey state (1-5 scales)
  const [sleepQuality, setSleepQuality] = useState<number>(4);
  const [fatigueLevel, setFatigueLevel] = useState<number>(2);
  const [workStress, setWorkStress] = useState<number>(2);
  const [moodWellbeing, setMoodWellbeing] = useState<number>(4);
  const [workLifeBalance, setWorkLifeBalance] = useState<number>(3);
  const [jobSatisfaction, setJobSatisfaction] = useState<number>(4);

  const [loading, setLoading] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const status = await wellnessApi.getCheckInStatus();
      setCheckInStatus(status);
    } catch (err) {
      console.warn('Could not fetch check-in status:', err);
    }
  };

  useEffect(() => {
    const fetchPersonalData = async () => {
      try {
        const [profile, timeline, status] = await Promise.all([
          personnelApi.getProfile(personnelId).catch(() => null),
          personnelApi.getTimeline(personnelId).catch(() => null),
          wellnessApi.getCheckInStatus().catch(() => null)
        ]);
        setHrProfile(profile);
        setTimelineData(timeline);
        setCheckInStatus(status);
      } catch (err) {
        console.error('Failed to load profile:', err);
      }
    };
    fetchPersonalData();
  }, [personnelId]);

  const handleSubmitCheckIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const res = await wellnessApi.submitCheckIn({
        sleep_quality: sleepQuality,
        fatigue_level: fatigueLevel,
        work_stress: workStress,
        mood_wellbeing: moodWellbeing,
        work_life_balance: workLifeBalance,
        job_satisfaction: jobSatisfaction
      });
      setSuccessMessage(res.message);
      fetchStatus();
    } catch (err: any) {
      console.error('Failed to submit check-in:', err);
      setError(err.response?.data?.detail || 'Failed to record check-in.');
    } finally {
      setLoading(false);
    }
  };

  const latestMonth = timelineData?.timeline[timelineData.timeline.length - 1];

  return (
    <div className="p-4 sm:p-6 space-y-5 max-w-5xl mx-auto">
      
      {/* Header Banner */}
      <div className="bg-white border-2 border-saathi-primary p-5 rounded-lg shadow-gov flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1 rounded bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
              <ShieldCheck className="w-4 h-4" />
            </span>
            <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-primary">
              Personal Welfare Portal
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-saathi-textDark">Personnel Service & Welfare Portal</h1>
          <p className="text-xs text-saathi-textMuted mt-0.5 max-w-xl">
            Logged in as <strong className="text-saathi-textDark font-mono font-bold">{personnelId}</strong> ({hrProfile?.job_role || 'Field Personnel'}, {hrProfile?.department || 'Operations'}).
          </p>
        </div>

        <div className="bg-saathi-bg border border-saathi-border p-3 rounded-lg flex items-center gap-3 shrink-0">
          <div className="p-2 rounded bg-white text-saathi-primary border border-saathi-border">
            <Lock className="w-4 h-4 text-saathi-primary" />
          </div>
          <div>
            <div className="text-xs font-bold text-saathi-textDark">Confidentiality Guarantee</div>
            <div className="text-[10px] text-saathi-textMuted">Restricted from unit commanders</div>
          </div>
        </div>
      </div>

      {/* Check-In Cycle Status & Follow-up Notice */}
      {checkInStatus && (
        <div className={`p-4 rounded-lg border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
          checkInStatus.follow_up_requested
            ? 'bg-amber-50 border-amber-300 text-amber-900'
            : checkInStatus.is_submitted
            ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
            : 'bg-saathi-bg border-saathi-border text-saathi-textDark'
        }`}>
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-md shrink-0 ${
              checkInStatus.follow_up_requested
                ? 'bg-amber-200 text-amber-800'
                : checkInStatus.is_submitted
                ? 'bg-emerald-200 text-emerald-800'
                : 'bg-saathi-bgAlt text-saathi-primary border border-saathi-border'
            }`}>
              {checkInStatus.follow_up_requested ? (
                <Bell className="w-5 h-5 animate-bounce" />
              ) : checkInStatus.is_submitted ? (
                <CheckCircle2 className="w-5 h-5" />
              ) : (
                <Clock className="w-5 h-5" />
              )}
            </div>
            <div>
              <div className="text-xs font-black uppercase tracking-wider">
                {checkInStatus.follow_up_requested
                  ? 'Monthly Check-In Follow-up Requested'
                  : checkInStatus.is_submitted
                  ? 'Monthly Check-In Submitted'
                  : 'Monthly Check-In Window Active'}
              </div>
              <p className="text-xs mt-0.5 opacity-90">
                {checkInStatus.message}
              </p>
            </div>
          </div>

          {!checkInStatus.is_submitted && (
            <button
              onClick={() => setActiveTab('survey')}
              className="px-3.5 py-1.5 bg-saathi-primary hover:bg-saathi-primaryDark text-white text-xs font-bold rounded shrink-0 shadow-xs transition"
            >
              Complete Check-In Form
            </button>
          )}
        </div>
      )}

      {/* Portal Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-saathi-border pb-2.5 overflow-x-auto">
        <button
          type="button"
          onClick={() => setActiveTab('companion')}
          className={`px-3.5 py-2 rounded text-xs font-bold flex items-center gap-2 transition-all cursor-pointer border ${
            activeTab === 'companion'
              ? 'bg-saathi-primary text-white border-saathi-primary shadow-xs'
              : 'bg-white border-saathi-border text-saathi-textMuted hover:text-saathi-textDark hover:bg-saathi-bg'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>AI Wellness Companion (Voice & Text)</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('survey')}
          className={`px-3.5 py-2 rounded text-xs font-bold flex items-center gap-2 transition-all cursor-pointer border ${
            activeTab === 'survey'
              ? 'bg-saathi-primary text-white border-saathi-primary shadow-xs'
              : 'bg-white border-saathi-border text-saathi-textMuted hover:text-saathi-textDark hover:bg-saathi-bg'
          }`}
        >
          <FileSpreadsheet className="w-4 h-4" />
          <span>Monthly Check-In Form</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('telemetry')}
          className={`px-3.5 py-2 rounded text-xs font-bold flex items-center gap-2 transition-all cursor-pointer border ${
            activeTab === 'telemetry'
              ? 'bg-saathi-primary text-white border-saathi-primary shadow-xs'
              : 'bg-white border-saathi-border text-saathi-textMuted hover:text-saathi-textDark hover:bg-saathi-bg'
          }`}
        >
          <Activity className="w-4 h-4" />
          <span>Service & Recovery Telemetry</span>
        </button>
      </div>

      {/* Tab 1: AI Wellness Companion */}
      {activeTab === 'companion' && (
        <WellnessCompanion personnelId={personnelId} />
      )}

      {/* Tab 2: Monthly Form Check-In */}
      {activeTab === 'survey' && (
        <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
          <div className="flex items-center justify-between mb-3.5 border-b border-saathi-border pb-2.5">
            <div>
              <h3 className="text-base font-bold text-saathi-textDark flex items-center gap-2">
                <HeartHandshake className="w-5 h-5 text-saathi-primary" />
                <span>Voluntary Monthly Wellness Survey</span>
              </h3>
              <p className="text-xs text-saathi-textMuted mt-0.5">
                Your confidential feedback informs supportive welfare planning. It is entirely voluntary and not a medical examination.
              </p>
            </div>
            <span className="text-[10px] font-mono font-bold text-emerald-800 bg-emerald-50 border border-emerald-300 px-2 py-0.5 rounded">
              CONFIDENTIAL DATA
            </span>
          </div>

          <form onSubmit={handleSubmitCheckIn} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* Sleep Quality */}
              <div className="p-3.5 rounded border border-saathi-border bg-saathi-bg space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-saathi-textDark">Sleep Quality (Last 30 Days)</label>
                  <span className="font-mono text-xs font-bold text-saathi-primary">{sleepQuality} / 5</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="5"
                  step="1"
                  value={sleepQuality}
                  onChange={(e) => setSleepQuality(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-white border border-saathi-border rounded appearance-none cursor-pointer accent-saathi-primary"
                />
                <div className="flex justify-between text-[10px] text-saathi-textMuted font-medium">
                  <span>1 (Very Poor / Broken)</span>
                  <span>5 (Restful & Consistent)</span>
                </div>
              </div>

              {/* Fatigue Level */}
              <div className="p-3.5 rounded border border-saathi-border bg-saathi-bg space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-saathi-textDark">Perceived Physical Fatigue</label>
                  <span className="font-mono text-xs font-bold text-saathi-saffron">{fatigueLevel} / 5</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="5"
                  step="1"
                  value={fatigueLevel}
                  onChange={(e) => setFatigueLevel(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-white border border-saathi-border rounded appearance-none cursor-pointer accent-saathi-saffron"
                />
                <div className="flex justify-between text-[10px] text-saathi-textMuted font-medium">
                  <span>1 (Energetic)</span>
                  <span>5 (Severe Exhaustion)</span>
                </div>
              </div>

              {/* Work Stress */}
              <div className="p-3.5 rounded border border-saathi-border bg-saathi-bg space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-saathi-textDark">Duty & Operational Strain</label>
                  <span className="font-mono text-xs font-bold text-saathi-primary">{workStress} / 5</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="5"
                  step="1"
                  value={workStress}
                  onChange={(e) => setWorkStress(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-white border border-saathi-border rounded appearance-none cursor-pointer accent-saathi-primary"
                />
                <div className="flex justify-between text-[10px] text-saathi-textMuted font-medium">
                  <span>1 (Easily Managed)</span>
                  <span>5 (Extremely Heavy)</span>
                </div>
              </div>

              {/* Mood & Wellbeing */}
              <div className="p-3.5 rounded border border-saathi-border bg-saathi-bg space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-saathi-textDark">General Morale & Wellbeing</label>
                  <span className="font-mono text-xs font-bold text-emerald-700">{moodWellbeing} / 5</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="5"
                  step="1"
                  value={moodWellbeing}
                  onChange={(e) => setMoodWellbeing(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-white border border-saathi-border rounded appearance-none cursor-pointer accent-emerald-600"
                />
                <div className="flex justify-between text-[10px] text-saathi-textMuted font-medium">
                  <span>1 (Low Morale)</span>
                  <span>5 (Strong & Positive)</span>
                </div>
              </div>
            </div>

            {successMessage && (
              <div className="p-3 rounded bg-emerald-50 border border-emerald-300 flex items-center gap-2 text-xs text-emerald-800 font-medium">
                <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-700" />
                <span>{successMessage}</span>
              </div>
            )}

            {error && (
              <div className="p-3 rounded bg-red-50 border border-red-300 flex items-center gap-2 text-xs text-red-800 font-medium">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-700" />
                <span>{error}</span>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2 rounded bg-saathi-saffron hover:bg-saathi-saffronHover disabled:bg-slate-300 text-white font-bold text-xs shadow-xs flex items-center gap-2 transition-colors cursor-pointer uppercase tracking-wider"
              >
                <Send className="w-4 h-4" />
                <span>{loading ? 'Submitting...' : 'Record Monthly Check-In'}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tab 3: Telemetry Cards */}
      {activeTab === 'telemetry' && latestMonth && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-4 rounded-lg bg-white border border-saathi-border shadow-gov">
              <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-textMuted">Monthly Duty Hours</span>
              <div className="text-2xl font-black text-saathi-textDark mt-1">{latestMonth.duty_hours.toFixed(1)} hrs</div>
              <span className="text-[10px] text-saathi-textSubtle">Baseline: {latestMonth.duty_hours_baseline?.toFixed(1) || '160.0'} hrs</span>
            </div>

            <div className="p-4 rounded-lg bg-white border border-saathi-border shadow-gov">
              <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-textMuted">Night Shifts</span>
              <div className="text-2xl font-black text-saathi-textDark mt-1">{latestMonth.night_shifts}</div>
              <span className="text-[10px] text-saathi-textSubtle">Baseline: {latestMonth.night_shifts_baseline?.toFixed(1) || '2.0'} shifts</span>
            </div>

            <div className="p-4 rounded-lg bg-white border border-emerald-300 shadow-gov">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-800">Rest & Recovery</span>
              <div className="text-2xl font-black text-emerald-700 mt-1">{latestMonth.rest_hours.toFixed(1)} hrs</div>
              <span className="text-[10px] text-saathi-textMuted">Monthly recorded rest</span>
            </div>

            <div className="p-4 rounded-lg bg-white border border-saathi-border shadow-gov">
              <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-textMuted">Leave Latency</span>
              <div className="text-2xl font-black text-saathi-primary mt-1">{latestMonth.days_since_prev_leave ?? 30} days</div>
              <span className="text-[10px] text-saathi-textSubtle">Since last leave</span>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-white border border-saathi-border space-y-1.5 shadow-gov">
            <h3 className="text-xs font-bold uppercase tracking-wider text-saathi-textDark">Deployment & Hardship Telemetry</h3>
            <p className="text-xs text-saathi-textMuted">
              Deployment status: <strong className="text-saathi-textDark">{latestMonth.is_deployed ? `${latestMonth.deployment_type} (Active)` : 'Base Station (Non-Deployed)'}</strong>
            </p>
            <p className="text-xs text-saathi-textMuted">
              Operational intensity level: <strong className="text-saathi-textDark">{latestMonth.operational_intensity ?? 1} / 5</strong>
            </p>
          </div>
        </div>
      )}

    </div>
  );
};
