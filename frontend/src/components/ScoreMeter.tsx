import React from 'react';
import { PriorityBadge } from './PriorityBadge';
import { PriorityTier } from '../types';
import { ShieldAlert, HelpCircle, CheckCircle2 } from 'lucide-react';

interface ScoreMeterProps {
  score: number | null;
  priority: PriorityTier;
  reliability: number;
  completeness: number;
  baselineMaturityMonths?: number;
  humanReviewRequired?: boolean;
}

export const ScoreMeter: React.FC<ScoreMeterProps> = ({
  score,
  priority,
  reliability,
  completeness,
  baselineMaturityMonths = 4,
  humanReviewRequired = false
}) => {
  const isInsufficient = priority === 'INSUFFICIENT_DATA' || score === null;
  const scoreVal = score ?? 0;

  const getMeterColor = () => {
    if (isInsufficient) return 'text-slate-400 stroke-slate-400';
    if (scoreVal < 30) return 'text-emerald-600 stroke-emerald-600';
    if (scoreVal < 55) return 'text-amber-600 stroke-amber-600';
    if (scoreVal < 75) return 'text-orange-600 stroke-orange-600';
    return 'text-red-600 stroke-red-600';
  };

  const getCardBorder = () => {
    if (isInsufficient) return 'border-saathi-border';
    if (scoreVal < 30) return 'border-emerald-300';
    if (scoreVal < 55) return 'border-amber-300';
    if (scoreVal < 75) return 'border-orange-300';
    return 'border-red-400';
  };

  return (
    <div className={`p-5 sm:p-6 rounded-lg border-2 bg-white ${getCardBorder()} shadow-gov relative overflow-hidden`}>
      <div className="flex flex-col md:flex-row items-center justify-between gap-6">
        
        {/* Left: Score Gauge */}
        <div className="flex items-center gap-6">
          <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
            {/* SVG Circular Meter */}
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="40"
                className="stroke-saathi-bgAlt"
                strokeWidth="9"
                fill="transparent"
              />
              <circle
                cx="50"
                cy="50"
                r="40"
                className={`transition-all duration-1000 ease-out ${getMeterColor()}`}
                strokeWidth="9"
                strokeDasharray="251.2"
                strokeDashoffset={251.2 - (251.2 * (isInsufficient ? 0 : scoreVal)) / 100}
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              {isInsufficient ? (
                <span className="text-xs font-bold text-saathi-textMuted">INCOMPLETE</span>
              ) : (
                <>
                  <span className="text-3xl font-black tracking-tight text-saathi-textDark">{scoreVal.toFixed(1)}</span>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-saathi-textMuted">Score / 100</span>
                </>
              )}
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-primary">
                Occupational Support Assessment
              </span>
            </div>
            <h3 className="text-lg font-bold text-saathi-textDark mb-2">Welfare Support Priority Score</h3>
            <PriorityBadge priority={priority} size="lg" />
            
            {humanReviewRequired && (
              <div className="mt-2.5 flex items-center gap-1.5 text-xs text-red-800 bg-red-50 border border-red-200 px-2.5 py-1 rounded">
                <ShieldAlert className="w-4 h-4 text-red-600 shrink-0" />
                <span className="font-bold">Human Welfare Review Recommended</span>
              </div>
            )}
          </div>
        </div>

        {/* Right: Reliability & Data Completeness Cards */}
        <div className="grid grid-cols-2 gap-3.5 w-full md:w-auto border-t md:border-t-0 md:border-l border-saathi-border md:pl-6">
          <div className="bg-saathi-bg p-3.5 rounded border border-saathi-border">
            <div className="flex items-center justify-between text-xs text-saathi-textMuted mb-1 font-semibold">
              <span>Prediction Reliability</span>
              <span title="Model certainty, completeness, and baseline history." className="cursor-help">
                <HelpCircle className="w-3.5 h-3.5 text-saathi-textSubtle" />
              </span>
            </div>
            <div className="text-xl font-black text-saathi-textDark">
              {(reliability * 100).toFixed(0)}%
            </div>
            <div className="w-full bg-white h-1.5 rounded-full mt-2 overflow-hidden border border-saathi-border">
              <div
                className="bg-saathi-primary h-full rounded-full transition-all duration-500"
                style={{ width: `${reliability * 100}%` }}
              />
            </div>
          </div>

          <div className="bg-saathi-bg p-3.5 rounded border border-saathi-border">
            <div className="flex items-center justify-between text-xs text-saathi-textMuted mb-1 font-semibold">
              <span>Data Completeness</span>
              <span title="Fraction of key operational & voluntary telemetry signals present." className="cursor-help">
                <HelpCircle className="w-3.5 h-3.5 text-saathi-textSubtle" />
              </span>
            </div>
            <div className="text-xl font-black text-saathi-textDark">
              {(completeness * 100).toFixed(0)}%
            </div>
            <div className="w-full bg-white h-1.5 rounded-full mt-2 overflow-hidden border border-saathi-border">
              <div
                className={`h-full rounded-full transition-all duration-500 ${completeness >= 0.70 ? 'bg-emerald-600' : completeness >= 0.35 ? 'bg-amber-500' : 'bg-red-500'}`}
                style={{ width: `${completeness * 100}%` }}
              />
            </div>
          </div>

          <div className="col-span-2 text-[11px] text-saathi-textMuted flex items-start gap-1.5 mt-0.5 bg-white p-2 rounded border border-saathi-border">
            <CheckCircle2 className="w-3.5 h-3.5 text-saathi-primary shrink-0 mt-0.5" />
            <span>
              Baseline maturity: <strong className="text-saathi-textDark">{baselineMaturityMonths} months</strong>. Model compares current metrics against personal historical norms.
            </span>
          </div>
        </div>

      </div>

      <div className="mt-4 pt-2.5 border-t border-saathi-border flex items-center justify-between text-[11px] text-saathi-textMuted font-medium">
        <span>Non-diagnostic decision support. Identifies welfare support priority; not a clinical or punitive assessment.</span>
        <span className="font-mono text-saathi-primary font-bold text-[10px]">VERIFIED ML ENGINE</span>
      </div>
    </div>
  );
};
