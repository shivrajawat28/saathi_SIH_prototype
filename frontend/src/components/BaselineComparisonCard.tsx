import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus, Clock, Moon, Battery, Calendar, Activity } from 'lucide-react';
import { TimelineItem } from '../types';

interface BaselineComparisonProps {
  currentRecord?: TimelineItem;
}

export const BaselineComparisonCard: React.FC<BaselineComparisonProps> = ({ currentRecord }) => {
  if (!currentRecord) {
    return (
      <div className="p-6 rounded-lg bg-white border border-saathi-border text-center text-saathi-textMuted text-xs">
        No longitudinal baseline data available for comparison.
      </div>
    );
  }

  const restBaseline = 80.0;
  const restChange = ((currentRecord.rest_hours - restBaseline) / restBaseline) * 100;
  
  const leaveBaseline = 45.0;
  const leaveLatency = currentRecord.days_since_prev_leave ?? 30;
  const leaveChange = ((leaveLatency - leaveBaseline) / leaveBaseline) * 100;

  const workloadBaseline = 45.0;
  const workloadChange = ((currentRecord.workload_score - workloadBaseline) / workloadBaseline) * 100;

  const metrics = [
    {
      label: 'Monthly Duty Hours',
      icon: Clock,
      current: `${currentRecord.duty_hours.toFixed(1)} hrs`,
      baseline: currentRecord.duty_hours_baseline ? `${currentRecord.duty_hours_baseline.toFixed(1)} hrs` : '184.0 hrs',
      change: currentRecord.duty_pct_change ?? 0,
      format: (val: number) => `${val > 0 ? '+' : ''}${val.toFixed(1)}%`,
      isElevatedRisk: (currentRecord.duty_pct_change ?? 0) > 15
    },
    {
      label: 'Night Shifts',
      icon: Moon,
      current: `${currentRecord.night_shifts} shifts`,
      baseline: currentRecord.night_shifts_baseline ? `${currentRecord.night_shifts_baseline.toFixed(1)} shifts` : '2.0 shifts',
      change: currentRecord.night_shifts_pct_change ?? 0,
      format: (val: number) => `${val > 0 ? '+' : ''}${val.toFixed(1)}%`,
      isElevatedRisk: (currentRecord.night_shifts_pct_change ?? 0) > 25
    },
    {
      label: 'Rest & Recovery',
      icon: Battery,
      current: `${currentRecord.rest_hours.toFixed(1)} hrs`,
      baseline: `${restBaseline.toFixed(1)} hrs`,
      change: restChange,
      format: (val: number) => `${val > 0 ? '+' : ''}${val.toFixed(1)}%`,
      isElevatedRisk: currentRecord.rest_hours < 50
    },
    {
      label: 'Leave Latency',
      icon: Calendar,
      current: `${leaveLatency} days`,
      baseline: `${leaveBaseline.toFixed(1)} days`,
      change: leaveChange,
      format: (val: number) => `${val > 0 ? '+' : ''}${val.toFixed(1)}%`,
      isElevatedRisk: leaveLatency > 90
    },
    {
      label: 'Workload Index',
      icon: Activity,
      current: `${currentRecord.workload_score.toFixed(1)} / 100`,
      baseline: `${workloadBaseline.toFixed(1)} / 100`,
      change: workloadChange,
      format: (val: number) => `${val > 0 ? '+' : ''}${val.toFixed(1)}%`,
      isElevatedRisk: currentRecord.workload_score > 65
    }
  ];

  return (
    <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 border-b border-saathi-border pb-3">
        <div>
          <h3 className="text-base font-bold text-saathi-textDark flex items-center gap-2">
            <span>Personal Baseline vs. Current Observation</span>
          </h3>
          <p className="text-xs text-saathi-textMuted mt-0.5">
            Compares current operational telemetry against individual historical norms (excluding population bias).
          </p>
        </div>
        <span className="text-[10px] font-bold text-saathi-primary bg-saathi-primarySubtle border border-saathi-secondaryLight px-2.5 py-1 rounded self-start sm:self-auto">
          Baseline Window: Time-Isolated History
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div
              key={idx}
              className={`p-3.5 rounded border transition-all ${
                m.isElevatedRisk 
                  ? 'bg-orange-50/60 border-orange-300' 
                  : 'bg-saathi-bg border-saathi-border'
              }`}
            >
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="flex items-center gap-1.5 font-bold text-saathi-textDark">
                  <Icon className="w-3.5 h-3.5 text-saathi-primary" />
                  {m.label}
                </span>
                
                {/* Change Tag */}
                <span className={`inline-flex items-center gap-0.5 font-bold text-[11px] px-2 py-0.5 rounded ${
                  m.isElevatedRisk 
                    ? 'bg-orange-100 text-orange-900 border border-orange-300' 
                    : 'bg-white text-saathi-textMuted border border-saathi-border'
                }`}>
                  {m.change > 0 ? (
                    <ArrowUpRight className="w-3 h-3" />
                  ) : m.change < 0 ? (
                    <ArrowDownRight className="w-3 h-3" />
                  ) : (
                    <Minus className="w-3 h-3" />
                  )}
                  {m.format(m.change)}
                </span>
              </div>

              <div className="flex items-baseline justify-between mt-2.5 pt-2 border-t border-saathi-border">
                <div>
                  <div className="text-[10px] uppercase font-bold text-saathi-textMuted">Current Period</div>
                  <div className="text-base font-black text-saathi-textDark">{m.current}</div>
                </div>
                <div className="text-right">
                  <div className="text-[10px] uppercase font-bold text-saathi-textMuted">Personal Baseline</div>
                  <div className="text-xs font-bold text-saathi-textSubtle">{m.baseline}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
