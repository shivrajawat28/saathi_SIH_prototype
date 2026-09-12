import React, { useState } from 'react';
import { Sliders, Sparkles, ArrowDownRight, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';
import { PriorityBadge } from './PriorityBadge';
import { simulationsApi } from '../api/simulations';
import { SimulationResponse } from '../types';

interface WhatIfSimulatorProps {
  personnelId: string;
  currentScore: number;
  currentPriority: string;
}

export const WhatIfSimulator: React.FC<WhatIfSimulatorProps> = ({
  personnelId,
  currentScore,
  currentPriority
}) => {
  const [reduceNightShifts, setReduceNightShifts] = useState<number>(8);
  const [reduceDutyHours, setReduceDutyHours] = useState<number>(40);
  const [grantRecoveryDays, setGrantRecoveryDays] = useState<number>(3);
  const [reduceOvertimeHours, setReduceOvertimeHours] = useState<number>(10);

  const [loading, setLoading] = useState<boolean>(false);
  const [simulationResult, setSimulationResult] = useState<SimulationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await simulationsApi.runSimulation(personnelId, {
        reduce_night_shifts: reduceNightShifts,
        reduce_duty_hours: reduceDutyHours,
        grant_recovery_days: grantRecoveryDays,
        reduce_overtime_hours: reduceOvertimeHours
      });
      setSimulationResult(res);
    } catch (err: any) {
      console.error('Simulation error:', err);
      setError(err.response?.data?.detail || 'Simulation service error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setReduceNightShifts(0);
    setReduceDutyHours(0);
    setGrantRecoveryDays(0);
    setReduceOvertimeHours(0);
    setSimulationResult(null);
    setError(null);
  };

  const applyCanonicalPreset = () => {
    setReduceNightShifts(8);
    setReduceDutyHours(40);
    setGrantRecoveryDays(3);
    setReduceOvertimeHours(10);
  };

  return (
    <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov relative overflow-hidden">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 border-b border-saathi-border pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
              <Sliders className="w-4 h-4" />
            </span>
            <h3 className="text-base font-bold text-saathi-textDark">What-If Welfare Simulator</h3>
          </div>
          <p className="text-xs text-saathi-textMuted mt-0.5">
            Simulate potential operational adjustments (reducing shifts, granting rest) and project scenario model response.
          </p>
        </div>
        <span className="text-[10px] font-mono font-bold text-saathi-primary bg-saathi-primarySubtle border border-saathi-secondaryLight px-2 py-0.5 rounded self-start sm:self-auto">
          SCENARIO SIMULATION
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Controls Section (7 cols) */}
        <div className="lg:col-span-7 space-y-3.5 bg-saathi-bg p-4 rounded border border-saathi-border">
          
          {/* Preset Bar */}
          <div className="flex items-center justify-between gap-2 pb-2 border-b border-saathi-border">
            <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-textMuted">Scenario Presets:</span>
            <button
              type="button"
              onClick={applyCanonicalPreset}
              className="text-xs font-bold text-saathi-primary hover:text-saathi-saffron underline underline-offset-2 cursor-pointer"
            >
              Apply Canonical Scenario (-40h, -8 shifts)
            </button>
          </div>

          {/* Slider 1: Night Shifts */}
          <div>
            <div className="flex items-center justify-between text-xs font-bold text-saathi-textDark mb-1">
              <span>Reduce Night Shifts</span>
              <span className="font-mono text-saathi-primary font-bold">-{reduceNightShifts} shifts</span>
            </div>
            <input
              type="range"
              min="0"
              max="14"
              step="1"
              value={reduceNightShifts}
              onChange={(e) => setReduceNightShifts(parseInt(e.target.value))}
              className="w-full h-1.5 bg-white border border-saathi-border rounded appearance-none cursor-pointer accent-saathi-primary"
            />
            <div className="flex justify-between text-[10px] text-saathi-textMuted mt-0.5 font-mono">
              <span>0 (None)</span>
              <span>-7 shifts</span>
              <span>-14 shifts</span>
            </div>
          </div>

          {/* Slider 2: Duty Hours */}
          <div>
            <div className="flex items-center justify-between text-xs font-bold text-saathi-textDark mb-1">
              <span>Reduce Monthly Duty Hours</span>
              <span className="font-mono text-saathi-primary font-bold">-{reduceDutyHours} hrs</span>
            </div>
            <input
              type="range"
              min="0"
              max="80"
              step="5"
              value={reduceDutyHours}
              onChange={(e) => setReduceDutyHours(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-white border border-saathi-border rounded appearance-none cursor-pointer accent-saathi-primary"
            />
            <div className="flex justify-between text-[10px] text-saathi-textMuted mt-0.5 font-mono">
              <span>0 hrs</span>
              <span>-40 hrs</span>
              <span>-80 hrs</span>
            </div>
          </div>

          {/* Slider 3: Recovery Leave Days */}
          <div>
            <div className="flex items-center justify-between text-xs font-bold text-saathi-textDark mb-1">
              <span>Grant Restorative Recovery Leave</span>
              <span className="font-mono text-emerald-700 font-bold">+{grantRecoveryDays} days</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="1"
              value={grantRecoveryDays}
              onChange={(e) => setGrantRecoveryDays(parseInt(e.target.value))}
              className="w-full h-1.5 bg-white border border-saathi-border rounded appearance-none cursor-pointer accent-emerald-600"
            />
            <div className="flex justify-between text-[10px] text-saathi-textMuted mt-0.5 font-mono">
              <span>0 days</span>
              <span>+5 days</span>
              <span>+10 days</span>
            </div>
          </div>

          {/* Slider 4: Overtime Hours */}
          <div>
            <div className="flex items-center justify-between text-xs font-bold text-saathi-textDark mb-1">
              <span>Curtail Overtime Deployment</span>
              <span className="font-mono text-saathi-primary font-bold">-{reduceOvertimeHours} hrs</span>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              step="2"
              value={reduceOvertimeHours}
              onChange={(e) => setReduceOvertimeHours(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-white border border-saathi-border rounded appearance-none cursor-pointer accent-saathi-primary"
            />
            <div className="flex justify-between text-[10px] text-saathi-textMuted mt-0.5 font-mono">
              <span>0 hrs</span>
              <span>-20 hrs</span>
              <span>-40 hrs</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2.5 pt-1">
            <button
              onClick={handleRunSimulation}
              disabled={loading}
              className="flex-1 py-2 rounded bg-saathi-primary hover:bg-saathi-primaryLight disabled:bg-saathi-primary/50 text-white font-bold text-xs shadow-xs flex items-center justify-center gap-2 transition-colors cursor-pointer"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Projecting Model Trajectory...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-saathi-saffron" />
                  <span>Simulate Operational Impact</span>
                </>
              )}
            </button>

            <button
              onClick={handleReset}
              disabled={loading}
              className="px-3.5 py-2 rounded bg-white hover:bg-saathi-bg border border-saathi-border text-saathi-textDark font-bold text-xs transition-colors cursor-pointer"
            >
              Reset
            </button>
          </div>

          {error && (
            <div className="text-xs text-red-700 bg-red-50 border border-red-200 p-2 rounded flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Results Section (5 cols) */}
        <div className="lg:col-span-5 flex flex-col justify-between bg-white p-4 rounded border border-saathi-border">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-saathi-primary">Projected Simulation Impact</span>

            {simulationResult ? (
              <div className="mt-3 space-y-3">
                <div className="grid grid-cols-2 gap-2.5">
                  <div className="p-2.5 rounded bg-saathi-bg border border-saathi-border text-center">
                    <span className="text-[10px] font-bold uppercase text-saathi-textMuted">Current Score</span>
                    <div className="text-xl font-black text-saathi-textDark mt-0.5">
                      {simulationResult.current_score.toFixed(1)}
                    </div>
                    <div className="mt-1">
                      <PriorityBadge priority={simulationResult.current_priority} size="sm" showLabel={false} />
                    </div>
                  </div>

                  <div className="p-2.5 rounded bg-emerald-50 border border-emerald-300 text-center">
                    <span className="text-[10px] font-bold uppercase text-emerald-800">Projected Score</span>
                    <div className="text-xl font-black text-emerald-800 mt-0.5">
                      {simulationResult.projected_score.toFixed(1)}
                    </div>
                    <div className="mt-1">
                      <PriorityBadge priority={simulationResult.projected_priority} size="sm" showLabel={false} />
                    </div>
                  </div>
                </div>

                {/* Score Delta Badge */}
                <div className="p-2.5 rounded bg-saathi-primarySubtle border border-saathi-secondaryLight flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs text-saathi-textDark font-bold">
                    <ArrowDownRight className="w-4 h-4 text-emerald-600" />
                    <span>Projected Score Reduction:</span>
                  </div>
                  <span className="text-sm font-black text-emerald-800 font-mono">
                    {simulationResult.projected_delta} pts
                  </span>
                </div>

                {/* Parameter Changes Summary */}
                <div className="text-xs text-saathi-textMuted space-y-1 bg-saathi-bg p-2.5 rounded border border-saathi-border">
                  <div className="font-bold text-saathi-textDark mb-1">Simulated Adjustments Applied:</div>
                  {simulationResult.parameter_changes.map((pc, i) => (
                    <div key={i} className="flex justify-between text-[11px]">
                      <span>{pc.factor.replace(/_/g, ' ')}:</span>
                      <span className="font-mono text-saathi-textDark font-bold">{pc.before} → {pc.after}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="my-auto py-10 text-center text-saathi-textMuted">
                <Sliders className="w-6 h-6 mx-auto mb-2 text-saathi-textSubtle" />
                <p className="text-xs leading-relaxed">
                  Adjust parameters and click <strong>Simulate Operational Impact</strong> to project model trajectory.
                </p>
              </div>
            )}
          </div>

          <div className="mt-3 pt-2.5 border-t border-saathi-border text-[10px] text-saathi-textMuted flex items-start gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-saathi-primary shrink-0 mt-0.5" />
            <span>
              <strong>Simulation Safeguard:</strong> Projected model response — not a causal guarantee. Simulation scenarios do not modify persistent personnel records.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
