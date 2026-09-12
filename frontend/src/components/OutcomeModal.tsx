import React, { useState } from 'react';
import { X, CheckCircle2, AlertTriangle, ArrowUpRight } from 'lucide-react';
import { interventionsApi } from '../api/interventions';
import { OutcomeResponse } from '../types';

interface OutcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  interventionId: string;
  onOutcomeRecorded: (outcome: OutcomeResponse) => void;
}

export const OutcomeModal: React.FC<OutcomeModalProps> = ({
  isOpen,
  onClose,
  interventionId,
  onOutcomeRecorded
}) => {
  const [outcomeStatus, setOutcomeStatus] = useState<'IMPROVED' | 'UNCHANGED' | 'ESCALATED'>('IMPROVED');
  const [followUpNotes, setFollowUpNotes] = useState<string>('');
  const [reviewDate, setReviewDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!followUpNotes.trim()) {
      setError('Please provide qualitative outcome assessment notes.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await interventionsApi.recordOutcome(interventionId, {
        outcome_status: outcomeStatus,
        follow_up_notes: followUpNotes,
        review_date: reviewDate
      });
      onOutcomeRecorded(res);
      onClose();
    } catch (err: any) {
      console.error('Failed to record outcome:', err);
      setError(err.response?.data?.detail || 'Failed to record outcome evaluation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="bg-white border-2 border-saathi-primary w-full max-w-md rounded-lg shadow-gov-lg overflow-hidden animate-in fade-in zoom-in duration-150">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-saathi-primary text-white border-b border-saathi-primaryDark">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Record Follow-up Outcome</h3>
            <p className="text-[11px] text-saathi-secondaryLight">Intervention ID: <span className="font-mono text-amber-300 font-bold">{interventionId}</span></p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-saathi-saffron p-1 rounded hover:bg-saathi-primaryDark transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 bg-saathi-bg">
          <div>
            <label className="block text-xs font-bold text-saathi-textDark uppercase tracking-wider mb-1.5">
              Outcome Evaluation Status
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setOutcomeStatus('IMPROVED')}
                className={`p-2.5 rounded border text-center transition-all ${
                  outcomeStatus === 'IMPROVED' 
                    ? 'bg-emerald-100 border-emerald-500 text-emerald-900 font-bold' 
                    : 'bg-white border-saathi-border text-saathi-textMuted hover:border-emerald-300'
                }`}
              >
                <CheckCircle2 className="w-4 h-4 mx-auto mb-1 text-emerald-700" />
                <span className="text-[11px] uppercase block">IMPROVED</span>
              </button>

              <button
                type="button"
                onClick={() => setOutcomeStatus('UNCHANGED')}
                className={`p-2.5 rounded border text-center transition-all ${
                  outcomeStatus === 'UNCHANGED' 
                    ? 'bg-amber-100 border-amber-500 text-amber-900 font-bold' 
                    : 'bg-white border-saathi-border text-saathi-textMuted hover:border-amber-300'
                }`}
              >
                <AlertTriangle className="w-4 h-4 mx-auto mb-1 text-amber-700" />
                <span className="text-[11px] uppercase block">UNCHANGED</span>
              </button>

              <button
                type="button"
                onClick={() => setOutcomeStatus('ESCALATED')}
                className={`p-2.5 rounded border text-center transition-all ${
                  outcomeStatus === 'ESCALATED' 
                    ? 'bg-red-100 border-red-500 text-red-900 font-bold' 
                    : 'bg-white border-saathi-border text-saathi-textMuted hover:border-red-300'
                }`}
              >
                <ArrowUpRight className="w-4 h-4 mx-auto mb-1 text-red-700" />
                <span className="text-[11px] uppercase block">ESCALATED</span>
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-saathi-textDark uppercase tracking-wider mb-1">
              Follow-up Review Date
            </label>
            <input
              type="date"
              value={reviewDate}
              onChange={(e) => setReviewDate(e.target.value)}
              className="w-full px-3 py-2 rounded border border-saathi-border bg-white text-saathi-textDark text-xs focus:outline-none focus:border-saathi-primary font-medium"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-saathi-textDark uppercase tracking-wider mb-1">
              Follow-up Observations & Notes
            </label>
            <textarea
              rows={3}
              value={followUpNotes}
              onChange={(e) => setFollowUpNotes(e.target.value)}
              placeholder="e.g., Post-leave check-in shows restored sleep rhythms and workload balance normalized."
              className="w-full px-3 py-2 rounded border border-saathi-border bg-white text-saathi-textDark text-xs focus:outline-none focus:border-saathi-primary resize-none placeholder:text-saathi-textSubtle font-medium"
            />
          </div>

          {error && (
            <div className="p-2.5 rounded border border-red-300 bg-red-50 text-xs text-red-700">
              {error}
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-saathi-border">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 text-xs font-bold text-saathi-textDark bg-white hover:bg-saathi-bg border border-saathi-border rounded transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-1.5 text-xs font-bold text-white bg-saathi-primary hover:bg-saathi-primaryLight rounded shadow-xs transition-colors disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Record Outcome'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
