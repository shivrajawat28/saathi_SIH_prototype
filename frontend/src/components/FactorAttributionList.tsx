import React from 'react';
import { TrendingUp, TrendingDown, HelpCircle, AlertCircle } from 'lucide-react';
import { TopFactor } from '../types';

interface FactorAttributionListProps {
  factors: TopFactor[];
}

export const FactorAttributionList: React.FC<FactorAttributionListProps> = ({ factors }) => {
  if (!factors || factors.length === 0) {
    return (
      <div className="p-5 rounded-lg bg-white border border-saathi-border text-center text-saathi-textMuted text-xs">
        No primary factor attributions recorded for this observation.
      </div>
    );
  }

  const maxContrib = Math.max(...factors.map(f => Math.abs(f.contribution)), 0.01);

  return (
    <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
      <div className="flex items-center justify-between mb-3 border-b border-saathi-border pb-2.5">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-saathi-textDark">Why Did This Score Change?</h3>
            <span title="Feature attribution computed via model explainer, highlighting top occupational drivers." className="cursor-help text-saathi-textSubtle">
              <HelpCircle className="w-3.5 h-3.5" />
            </span>
          </div>
          <p className="text-xs text-saathi-textMuted mt-0.5">
            Transparent occupational factor contributions driving the Welfare Support Priority.
          </p>
        </div>
        <span className="text-[10px] font-mono font-bold text-saathi-primary bg-saathi-primarySubtle border border-saathi-secondaryLight px-2 py-0.5 rounded">
          EXPLAINABLE AI
        </span>
      </div>

      <div className="space-y-3 mt-4">
        {factors.map((factor, idx) => {
          const isIncrease = factor.direction === 'increase';
          const relativePercent = Math.min(100, Math.round((Math.abs(factor.contribution) / maxContrib) * 100));

          return (
            <div key={idx} className="p-3 rounded border border-saathi-border bg-saathi-bg">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <div className={`p-1 rounded ${
                    isIncrease 
                      ? 'bg-orange-100 text-orange-800 border border-orange-200' 
                      : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                  }`}>
                    {isIncrease ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                  </div>
                  <div>
                    <span className="text-xs font-bold text-saathi-textDark">{factor.factor}</span>
                    <span className="ml-1.5 text-[11px] text-saathi-textMuted capitalize">({factor.direction})</span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono font-bold text-saathi-primary">
                    {Math.round(factor.contribution * 100)}% impact
                  </span>
                </div>
              </div>

              {/* Progress Contribution Bar */}
              <div className="w-full bg-white h-2 rounded-full overflow-hidden border border-saathi-border">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isIncrease 
                      ? 'bg-gradient-to-r from-amber-500 to-red-600' 
                      : 'bg-gradient-to-r from-emerald-600 to-teal-700'
                  }`}
                  style={{ width: `${relativePercent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 p-2.5 rounded bg-saathi-primarySubtle border border-saathi-secondaryLight flex items-start gap-2 text-xs text-saathi-textMuted">
        <AlertCircle className="w-4 h-4 text-saathi-primary shrink-0 mt-0.5" />
        <span className="text-[11px] leading-tight">
          <strong>Ethical Notice:</strong> Factor attributions describe observable operational telemetry deviations from baseline. They represent operational indicators, not clinical or psychological conclusions.
        </span>
      </div>
    </div>
  );
};
