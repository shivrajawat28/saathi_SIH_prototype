import React, { useState, useEffect } from 'react';
import {
  HeartHandshake,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Clock,
  UserCheck,
  FileEdit
} from 'lucide-react';
import { wellnessApi } from '../api/wellness';
import { CompanionConversationSummary } from '../types';

interface VoluntaryConversationCardProps {
  personnelId: string;
  onTakeAction?: () => void;
}

export const VoluntaryConversationCard: React.FC<VoluntaryConversationCardProps> = ({
  personnelId,
  onTakeAction
}) => {
  const [conversations, setConversations] = useState<CompanionConversationSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [reviewNotes, setReviewNotes] = useState<string>('');
  const [reviewing, setReviewing] = useState<boolean>(false);
  const [reviewSuccess, setReviewSuccess] = useState<string | null>(null);

  const fetchConversations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await wellnessApi.getPersonnelCompanionSignals(personnelId);
      setConversations(data);
      if (data.length > 0 && data[0].welfare_officer_notes) {
        setReviewNotes(data[0].welfare_officer_notes);
      }
    } catch (err: any) {
      console.error('Failed to load companion conversation signals:', err);
      setError(err.response?.data?.detail || 'Failed to load voluntary check-in signals.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, [personnelId]);

  const handleSaveReview = async (status: string) => {
    if (conversations.length === 0) return;
    const latest = conversations[0];
    setReviewing(true);
    setReviewSuccess(null);

    try {
      const updated = await wellnessApi.reviewCompanionConversation(latest.conversation_id, {
        status: status,
        notes: reviewNotes.trim() || undefined
      });
      setConversations([updated, ...conversations.slice(1)]);
      setReviewSuccess(`Check-in review marked as ${status}.`);
    } catch (err: any) {
      console.error('Failed to update review:', err);
    } finally {
      setReviewing(false);
    }
  };

  if (loading) {
    return (
      <div className="p-5 rounded-lg bg-white border border-saathi-border flex items-center justify-center gap-2 text-xs text-saathi-textMuted">
        <RefreshCw className="w-4 h-4 animate-spin text-saathi-primary" />
        <span>Loading voluntary check-in signals...</span>
      </div>
    );
  }

  const latestConv = conversations.length > 0 ? conversations[0] : null;
  const signals = latestConv?.structured_signals;

  return (
    <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-saathi-border">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
            <HeartHandshake className="w-5 h-5 text-saathi-primary" />
          </div>
          <div>
            <h3 className="text-base font-bold text-saathi-textDark flex items-center gap-2">
              <span>Voluntary Wellness Conversation</span>
              <span className="text-[10px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-300 px-2 py-0.5 rounded">
                CONFIDENTIAL
              </span>
            </h3>
            <p className="text-xs text-saathi-textMuted mt-0.5">
              Self-reported voluntary check-in signals extracted via SAATHI Wellness Companion.
            </p>
          </div>
        </div>

        {latestConv && (
          <div className="flex items-center gap-2 text-xs text-saathi-textMuted font-mono">
            <Clock className="w-3.5 h-3.5" />
            <span>{new Date(latestConv.created_at).toLocaleDateString()}</span>
            <span className={`px-2 py-0.2 rounded text-[10px] font-bold uppercase border ${
              latestConv.status === 'ACKNOWLEDGED'
                ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                : 'bg-amber-50 text-amber-800 border-amber-300'
            }`}>
              {latestConv.status.replace(/_/g, ' ')}
            </span>
          </div>
        )}
      </div>

      {latestConv && signals ? (
        <div className="space-y-3.5">
          {/* Main Interpretation Box */}
          <div className="p-3.5 rounded border border-saathi-border bg-saathi-bg space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-saathi-textDark flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-saathi-primary" />
                <span>AI Non-Clinical Interpretation</span>
              </span>
              <span className="text-[10px] font-mono text-saathi-textMuted">
                Signal Confidence: {(latestConv.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-xs text-saathi-textDark italic leading-relaxed">
              "{latestConv.ai_summary}"
            </p>
          </div>

          {/* Signals Matrix Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
            <div className="p-3 rounded border border-saathi-border bg-white">
              <span className="text-[10px] text-saathi-textMuted block font-bold uppercase">Self-Reported Fatigue</span>
              <span className={`text-sm font-black mt-0.5 block ${
                signals.fatigue === 'Elevated' ? 'text-orange-700' : 'text-saathi-textDark'
              }`}>
                {signals.fatigue}
              </span>
            </div>

            <div className="p-3 rounded border border-saathi-border bg-white">
              <span className="text-[10px] text-saathi-textMuted block font-bold uppercase">Sleep Difficulty</span>
              <span className={`text-sm font-black mt-0.5 block ${
                signals.sleep_difficulty === 'Elevated' ? 'text-orange-700' : 'text-saathi-textDark'
              }`}>
                {signals.sleep_difficulty}
              </span>
            </div>

            <div className="p-3 rounded border border-saathi-border bg-white">
              <span className="text-[10px] text-saathi-textMuted block font-bold uppercase">Perceived Duty Pressure</span>
              <span className={`text-sm font-black mt-0.5 block ${
                signals.workload_pressure === 'Elevated' ? 'text-orange-700' : 'text-saathi-textDark'
              }`}>
                {signals.workload_pressure}
              </span>
            </div>

            <div className="p-3 rounded border border-saathi-border bg-white">
              <span className="text-[10px] text-saathi-textMuted block font-bold uppercase">Valence & Coping</span>
              <span className="text-sm font-black text-saathi-textDark mt-0.5 block">
                {signals.sentiment_valence}
              </span>
            </div>
          </div>

          {/* Positive Resilience & Longitudinal Baseline */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded border border-emerald-200 bg-emerald-50/50 space-y-1">
              <span className="text-[11px] font-bold text-emerald-800 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Positive Resilience & Strengths</span>
              </span>
              {signals.positive_resilience_indicators && signals.positive_resilience_indicators.length > 0 ? (
                <div className="space-y-0.5 pt-1">
                  {signals.positive_resilience_indicators.map((ind, i) => (
                    <div key={i} className="text-[11px] text-emerald-900 font-medium">
                      • {ind}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-[11px] text-saathi-textMuted pt-1">No explicit positive coping affirmations noted.</p>
              )}
            </div>

            <div className="p-3 rounded border border-saathi-border bg-saathi-bg space-y-1">
              <span className="text-[11px] font-bold text-saathi-textDark flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-saathi-primary" />
                <span>Change vs Previous Check-In</span>
              </span>
              <p className="text-[11px] text-saathi-textMuted pt-1 leading-relaxed">
                {latestConv.change_vs_previous || 'Initial baseline voluntary check-in.'}
              </p>
              {latestConv.welfare_signal_impact && (
                <div className="text-[10px] font-mono text-saathi-saffron font-bold pt-1">
                  {latestConv.welfare_signal_impact}
                </div>
              )}
            </div>
          </div>

          {/* Welfare Officer Action & Notes */}
          <div className="p-3.5 rounded border border-saathi-border bg-white space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-saathi-textDark flex items-center gap-1.5">
                <FileEdit className="w-3.5 h-3.5 text-saathi-primary" />
                <span>Welfare Officer Review & Supportive Outreach</span>
              </span>
              {latestConv.reviewed_by && (
                <span className="text-[10px] text-saathi-textMuted font-mono">
                  Reviewed by {latestConv.reviewed_by} on {latestConv.reviewed_at ? new Date(latestConv.reviewed_at).toLocaleDateString() : ''}
                </span>
              )}
            </div>

            <textarea
              rows={2}
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              placeholder="Record officer review notes, scheduled supportive conversation, or rest recommendations..."
              className="w-full bg-saathi-bg border border-saathi-border rounded p-2.5 text-xs text-saathi-textDark placeholder-saathi-textSubtle focus:bg-white focus:outline-none focus:border-saathi-primary transition-colors resize-none"
            />

            <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleSaveReview('ACKNOWLEDGED')}
                  disabled={reviewing}
                  className="px-3 py-1.5 rounded bg-saathi-primary hover:bg-saathi-primaryLight text-white font-bold text-xs transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
                >
                  <UserCheck className="w-3.5 h-3.5" />
                  <span>Acknowledge & Save Notes</span>
                </button>

                {onTakeAction && (
                  <button
                    type="button"
                    onClick={onTakeAction}
                    className="px-3 py-1.5 rounded bg-saathi-saffron hover:bg-saathi-saffronHover text-white font-bold text-xs transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
                  >
                    <span>Record Formal Welfare Action</span>
                  </button>
                )}
              </div>

              {reviewSuccess && (
                <span className="text-xs text-emerald-700 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{reviewSuccess}</span>
                </span>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="p-6 rounded border border-saathi-border bg-saathi-bg text-center text-saathi-textMuted text-xs">
          No voluntary wellness conversations recorded yet for this personnel.
        </div>
      )}
    </div>
  );
};
