import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { TimelineItem } from '../types';

interface TimelineChartProps {
  timeline: TimelineItem[];
  selectedMonthIdx?: number;
  onSelectMonth?: (monthIdx: number) => void;
}

export const TimelineChart: React.FC<TimelineChartProps> = ({
  timeline,
  selectedMonthIdx,
  onSelectMonth
}) => {
  const [metricView, setMetricView] = useState<'workload' | 'score' | 'recovery'>('workload');

  const chartData = timeline.map((item) => ({
    month: `M${item.month_idx}`,
    month_idx: item.month_idx,
    date: item.date,
    duty_hours: item.duty_hours,
    duty_baseline: item.duty_hours_baseline ?? 160,
    night_shifts: item.night_shifts,
    rest_hours: item.rest_hours,
    workload_score: item.workload_score,
    support_score: item.support_score ?? 20,
    priority: item.support_priority ?? 'GREEN'
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white border-2 border-saathi-primary p-3 rounded shadow-gov-md text-xs space-y-1">
          <div className="font-bold text-saathi-textDark flex items-center justify-between gap-4 border-b border-saathi-border pb-1">
            <span>Month {data.month_idx} ({data.date})</span>
            <span className={`px-2 py-0.2 rounded text-[10px] font-bold ${
              data.priority === 'RED' 
                ? 'bg-red-100 text-red-800 border border-red-300' 
                : data.priority === 'ORANGE' 
                ? 'bg-orange-100 text-orange-800 border border-orange-300' 
                : data.priority === 'YELLOW' 
                ? 'bg-amber-100 text-amber-800 border border-amber-300' 
                : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
            }`}>
              {data.priority}
            </span>
          </div>
          <div className="text-saathi-textMuted">
            Duty Hours: <strong className="text-saathi-textDark">{data.duty_hours.toFixed(1)} hrs</strong> (Baseline: {data.duty_baseline.toFixed(1)})
          </div>
          <div className="text-saathi-textMuted">
            Night Shifts: <strong className="text-saathi-textDark">{data.night_shifts}</strong>
          </div>
          <div className="text-saathi-textMuted">
            Rest Hours: <strong className="text-saathi-textDark">{data.rest_hours.toFixed(1)} hrs</strong>
          </div>
          <div className="text-saathi-primary font-bold pt-1 border-t border-saathi-border">
            Support Priority Score: {data.support_score.toFixed(1)} / 100
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 border-b border-saathi-border pb-3">
        <div>
          <h3 className="text-base font-bold text-saathi-textDark">12-Month Longitudinal Telemetry Timeline</h3>
          <p className="text-xs text-saathi-textMuted mt-0.5">
            Sequential monthly tracking comparing observed metrics against rolling individual baseline.
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex bg-saathi-bg p-1 rounded border border-saathi-border self-start sm:self-auto">
          <button
            onClick={() => setMetricView('workload')}
            className={`px-3 py-1 rounded text-xs font-bold transition-all ${
              metricView === 'workload' 
                ? 'bg-saathi-primary text-white shadow-xs' 
                : 'text-saathi-textMuted hover:text-saathi-primary'
            }`}
          >
            Duty & Shifts
          </button>
          <button
            onClick={() => setMetricView('score')}
            className={`px-3 py-1 rounded text-xs font-bold transition-all ${
              metricView === 'score' 
                ? 'bg-saathi-primary text-white shadow-xs' 
                : 'text-saathi-textMuted hover:text-saathi-primary'
            }`}
          >
            Support Score
          </button>
          <button
            onClick={() => setMetricView('recovery')}
            className={`px-3 py-1 rounded text-xs font-bold transition-all ${
              metricView === 'recovery' 
                ? 'bg-saathi-primary text-white shadow-xs' 
                : 'text-saathi-textMuted hover:text-saathi-primary'
            }`}
          >
            Rest & Recovery
          </button>
        </div>
      </div>

      <div className="h-68 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} onClick={(e: any) => e?.activePayload && onSelectMonth?.(e.activePayload[0].payload.month_idx)}>
            <CartesianGrid strokeDasharray="3 3" stroke="#D5DFD8" opacity={0.7} />
            <XAxis dataKey="month" stroke="#4B6358" fontSize={11} tickLine={false} />
            <YAxis stroke="#4B6358" fontSize={11} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px', color: '#10231B' }} />

            {metricView === 'workload' && (
              <>
                <Bar dataKey="night_shifts" name="Night Shifts" fill="#E65100" radius={[3, 3, 0, 0]} maxBarSize={24} />
                <Line type="monotone" dataKey="duty_hours" name="Duty Hours (Observed)" stroke="#1B4D3E" strokeWidth={2.5} dot={{ r: 3.5, fill: '#1B4D3E' }} />
                <Line type="monotone" dataKey="duty_baseline" name="Duty Baseline" stroke="#6B857A" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
              </>
            )}

            {metricView === 'score' && (
              <>
                <Line
                  type="monotone"
                  dataKey="support_score"
                  name="Welfare Support Score (0-100)"
                  stroke="#B91C1C"
                  strokeWidth={3}
                  dot={{ r: 4, stroke: '#991B1B', strokeWidth: 1, fill: '#B91C1C' }}
                />
              </>
            )}

            {metricView === 'recovery' && (
              <>
                <Line type="monotone" dataKey="rest_hours" name="Rest Hours (Monthly)" stroke="#15803D" strokeWidth={2.5} dot={{ r: 3.5, fill: '#15803D' }} />
                <Line type="monotone" dataKey="workload_score" name="Workload Index" stroke="#D97706" strokeWidth={2} dot={{ r: 3.5, fill: '#D97706' }} />
              </>
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Month Selector */}
      <div className="mt-4 pt-3 border-t border-saathi-border flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs text-saathi-textMuted font-bold">Select observation month:</span>
        <div className="flex flex-wrap gap-1">
          {timeline.map((item) => (
            <button
              key={item.month_idx}
              onClick={() => onSelectMonth?.(item.month_idx)}
              className={`px-2.5 py-0.5 text-xs font-bold rounded border transition-all ${
                selectedMonthIdx === item.month_idx
                  ? 'bg-saathi-primary border-saathi-primary text-white shadow-xs'
                  : 'bg-saathi-bg border-saathi-border text-saathi-textMuted hover:border-saathi-primary'
              }`}
            >
              M{item.month_idx}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
