import React from 'react';
import { ShieldCheck, HeartHandshake, CalendarClock, Stethoscope, ArrowRight, CheckCircle } from 'lucide-react';
import { WelfareRecommendation } from '../types';

interface RecommendationListProps {
  recommendations: WelfareRecommendation[];
  onTakeAction?: (rec: WelfareRecommendation) => void;
}

export const RecommendationList: React.FC<RecommendationListProps> = ({
  recommendations,
  onTakeAction
}) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="p-5 rounded-lg bg-white border border-saathi-border text-center text-saathi-textMuted text-xs">
        No active welfare recommendations. Routine monitoring in progress.
      </div>
    );
  }

  const getRecIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'WORKLOAD_REVIEW':
        return CalendarClock;
      case 'RECOVERY_LEAVE':
        return HeartHandshake;
      case 'WELFARE_CHECK_IN':
        return ShieldCheck;
      case 'COUNSELLING_REFERRAL':
        return Stethoscope;
      default:
        return CheckCircle;
    }
  };

  const getPriorityStyle = (priority: string) => {
    switch (priority.toUpperCase()) {
      case 'HIGH':
        return 'bg-red-50 text-red-800 border-red-300';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-800 border-amber-300';
      default:
        return 'bg-emerald-50 text-emerald-800 border-emerald-300';
    }
  };

  return (
    <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
      <div className="flex items-center justify-between mb-3 border-b border-saathi-border pb-2.5">
        <div>
          <h3 className="text-base font-bold text-saathi-textDark">Recommended Welfare Actions</h3>
          <p className="text-xs text-saathi-textMuted mt-0.5">
            Deterministic, non-punitive support measures generated for authorized welfare officers.
          </p>
        </div>
        <span className="text-[10px] font-mono font-bold text-saathi-primary bg-saathi-primarySubtle border border-saathi-secondaryLight px-2 py-0.5 rounded">
          DECISION SUPPORT
        </span>
      </div>

      <div className="space-y-3 mt-4">
        {recommendations.map((rec, idx) => {
          const Icon = getRecIcon(rec.type);
          const priorityStyle = getPriorityStyle(rec.priority);

          return (
            <div
              key={idx}
              className="p-3.5 rounded border border-saathi-border bg-saathi-bg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition-colors hover:border-saathi-primary"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 rounded bg-white text-saathi-primary border border-saathi-border shrink-0 mt-0.5 sm:mt-0">
                  <Icon className="w-4 h-4 text-saathi-primary" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-xs font-bold text-saathi-textDark">
                      {rec.type.replace(/_/g, ' ')}
                    </h4>
                    <span className={`text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.2 rounded border ${priorityStyle}`}>
                      {rec.priority} Priority
                    </span>
                  </div>
                  <p className="text-xs text-saathi-textMuted leading-relaxed max-w-xl">
                    {rec.reason}
                  </p>
                </div>
              </div>

              {onTakeAction && (
                <button
                  onClick={() => onTakeAction(rec)}
                  className="shrink-0 flex items-center gap-1 text-xs font-bold text-white bg-saathi-primary hover:bg-saathi-primaryLight px-3 py-1.5 rounded transition-colors self-end sm:self-center shadow-xs"
                >
                  <span>Initiate Action</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
