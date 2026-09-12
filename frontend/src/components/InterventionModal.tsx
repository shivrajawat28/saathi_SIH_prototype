import React, { useState } from 'react';
import { X, ShieldAlert, HeartHandshake, Calendar } from 'lucide-react';
import { interventionsApi } from '../api/interventions';
import { InterventionResponse } from '../types';

interface InterventionModalProps {
  isOpen: boolean;
  onClose: () => void;
  personnelId: string;
  defaultType?: string;
  onInterventionCreated: (intervention: InterventionResponse) => void;
}

export const InterventionModal: React.FC<InterventionModalProps> = ({
  isOpen,
  onClose,
  personnelId,
  defaultType = 'WORKLOAD_REVIEW',
  onInterventionCreated
}) => {
  const [interventionType, setInterventionType] = useState<string>(defaultType);
  const [actionSummary, setActionSummary] = useState<string>('');
  const [interventionDate, setInterventionDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actionSummary.trim()) {
      setError('Please provide a brief action summary description.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await interventionsApi.createIntervention({
        personnel_id: personnelId,
        intervention_type: interventionType,
        action_summary: actionSummary,
        intervention_date: interventionDate
      });
      onInterventionCreated(res);
      onClose();
    } catch (err: any) {
      console.error('Failed to create intervention:', err);
      setError(err.response?.data?.detail || 'Failed to record intervention. Please check permissions.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="bg-white border-2 border-saathi-primary w-full max-w-lg rounded-lg shadow-gov-lg overflow-hidden animate-in fade-in zoom-in duration-150">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-saathi-primary text-white border-b border-saathi-primaryDark">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded bg-saathi-primaryDark text-saathi-saffron border border-saathi-primaryLight">
              <HeartHandshake className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Record Welfare Support Action</h3>
              <p className="text-[11px] text-saathi-secondaryLight">Personnel ID: <span className="font-mono text-amber-300 font-bold">{personnelId}</span></p>
            </div>
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
            <label className="block text-xs font-bold text-saathi-textDark uppercase tracking-wider mb-1">
              Intervention Measure Type
            </label>
            <select
              value={interventionType}
              onChange={(e) => setInterventionType(e.target.value)}
              className="w-full px-3 py-2 rounded border border-saathi-border bg-white text-saathi-textDark text-xs focus:outline-none focus:border-saathi-primary font-medium"
            >
              <option value="WORKLOAD_REVIEW">Workload Review & Shift Balancing</option>
              <option value="RECOVERY_LEAVE">Restorative Recovery Leave Authorization</option>
              <option value="WELFARE_CHECK_IN">Authorized Welfare Officer 1-on-1 Check-in</option>
              <option value="COUNSELLING_REFERRAL">Voluntary Counselling & Support Referral</option>
              <option value="SCHEDULE_ADJUSTMENT">Operational Rhythm Stabilization</option>
              <option value="FOLLOW_UP_ASSESSMENT">Scheduled 14-Day Welfare Follow-up</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-saathi-textDark uppercase tracking-wider mb-1">
              Action Date
            </label>
            <div className="relative">
              <input
                type="date"
                value={interventionDate}
                onChange={(e) => setInterventionDate(e.target.value)}
                className="w-full px-3 py-2 rounded border border-saathi-border bg-white text-saathi-textDark text-xs focus:outline-none focus:border-saathi-primary font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-saathi-textDark uppercase tracking-wider mb-1">
              Action Summary & Operational Notes
            </label>
            <textarea
              rows={4}
              value={actionSummary}
              onChange={(e) => setActionSummary(e.target.value)}
              placeholder="e.g., Reviewed consecutive night duty logs; authorized 3 days rest rotation and scheduled follow-up check-in."
              className="w-full px-3 py-2 rounded border border-saathi-border bg-white text-saathi-textDark text-xs focus:outline-none focus:border-saathi-primary resize-none placeholder:text-saathi-textSubtle font-medium"
            />
          </div>

          <div className="p-2.5 rounded bg-saathi-primarySubtle border border-saathi-secondaryLight text-[11px] text-saathi-textMuted flex items-start gap-2">
            <ShieldAlert className="w-4 h-4 text-saathi-primary shrink-0 mt-0.5" />
            <span className="leading-tight">
              All recorded interventions are strictly non-punitive and logged immutably for closed-loop follow-up verification.
            </span>
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
              {loading ? 'Recording...' : 'Record Support Action'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
