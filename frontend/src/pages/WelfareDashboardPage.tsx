import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Search,
  Filter,
  ArrowUpRight,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  RefreshCw,
  Sparkles,
  HeartHandshake,
  CheckCircle2,
  Calendar,
  Layers,
  Activity
} from 'lucide-react';
import { PriorityBadge } from '../components/PriorityBadge';
import { predictionsApi } from '../api/predictions';
import { analyticsApi } from '../api/analytics';
import { BatchTriageItem, PriorityDistributionItem } from '../types';

export const WelfareDashboardPage: React.FC = () => {
  const [triageItems, setTriageItems] = useState<BatchTriageItem[]>([]);
  const [priorityDist, setPriorityDist] = useState<PriorityDistributionItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL');

  const navigate = useNavigate();

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [triageRes, overviewRes] = await Promise.all([
        predictionsApi.getBatchTriage(100),
        analyticsApi.getCommanderOverview()
      ]);
      setTriageItems(triageRes);
      setPriorityDist(overviewRes.priority_distribution);
    } catch (err) {
      console.error('Failed to load triage items:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const filteredItems = triageItems.filter((item) => {
    const matchesSearch =
      item.personnel_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.department && item.department.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesFilter = selectedFilter === 'ALL' || item.priority === selectedFilter;
    return matchesSearch && matchesFilter;
  });

  const getKpiCount = (priority: string) => {
    const found = priorityDist.find((p) => p.priority === priority);
    return found ? found.count : 0;
  };

  return (
    <div className="p-4 sm:p-6 space-y-5 max-w-7xl mx-auto">
      
      {/* Top Banner & Header */}
      <div className="bg-white border-2 border-saathi-primary rounded-lg shadow-gov p-5 sm:p-6 relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="p-1 rounded bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
                <ShieldCheck className="w-4 h-4" />
              </span>
              <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-primary">
                Authorized Welfare Officer Portal
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black text-saathi-textDark">
              Personnel Welfare Support & Triage Overview
            </h1>
            <p className="text-xs text-saathi-textMuted mt-1 max-w-2xl leading-relaxed">
              Objective occupational change detection and continuous support score prioritization for non-punitive welfare planning.
            </p>
          </div>

          {/* Demo Scenario Walkthrough */}
          <div className="bg-saathi-bg border border-saathi-border p-3.5 rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded bg-amber-100 text-saathi-saffron border border-amber-200">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-bold text-saathi-textDark">Canonical Demo Case</div>
                <div className="text-[10px] text-saathi-textMuted">P-000013 (Strain Surge) vs P-000001 (Stable)</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigate('/personnel/P-000013')}
                className="px-3 py-1.5 rounded bg-saathi-primary hover:bg-saathi-primaryLight text-white text-xs font-bold flex items-center gap-1 shadow-xs transition-colors"
              >
                <span>Inspect P-000013 (88.1 RED)</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => navigate('/personnel/P-000001')}
                className="px-2.5 py-1.5 rounded bg-white hover:bg-saathi-bg border border-saathi-border text-emerald-800 text-xs font-bold flex items-center gap-1 transition-colors"
              >
                <span>P-000001 (GREEN)</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Proactive Automated Welfare Alerts */}
      <div className="p-4 rounded-lg bg-white border border-saathi-border shadow-gov">
        <div className="flex items-center justify-between mb-3 border-b border-saathi-border pb-2">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded bg-amber-50 text-amber-700 border border-amber-200">
              <ShieldAlert className="w-4 h-4" />
            </span>
            <span className="text-xs font-bold text-saathi-textDark uppercase tracking-wider">
              Priority Emerging Welfare Concerns (Action Required)
            </span>
          </div>
          <span className="text-[10px] font-bold text-saathi-saffron bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded">
            3 Active Welfare Alerts
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div 
            onClick={() => navigate('/personnel/P-000013')}
            className="p-3 rounded border border-red-200 bg-red-50/50 hover:bg-red-50 cursor-pointer transition-colors"
          >
            <div className="flex items-center justify-between text-xs font-bold text-red-800 mb-1">
              <span className="font-mono">P-000013</span>
              <span className="bg-red-100 border border-red-300 text-red-800 px-1.5 py-0.2 rounded text-[10px]">Priority Surge: 88.1 RED</span>
            </div>
            <p className="text-[11px] text-saathi-textMuted">
              Extended leave gap (302d) & night shift surge (14 shifts) — Proactive review recommended.
            </p>
          </div>

          <div 
            onClick={() => navigate('/personnel/P-000081')}
            className="p-3 rounded border border-orange-200 bg-orange-50/50 hover:bg-orange-50 cursor-pointer transition-colors"
          >
            <div className="flex items-center justify-between text-xs font-bold text-orange-800 mb-1">
              <span className="font-mono">P-000081</span>
              <span className="bg-orange-100 border border-orange-300 text-orange-800 px-1.5 py-0.2 rounded text-[10px]">Reduced Recovery: 88.0 RED</span>
            </div>
            <p className="text-[11px] text-saathi-textMuted">
              Persistent reduced recovery detected below personal baseline threshold.
            </p>
          </div>

          <div 
            onClick={() => navigate('/personnel/P-000114')}
            className="p-3 rounded border border-amber-200 bg-amber-50/50 hover:bg-amber-50 cursor-pointer transition-colors"
          >
            <div className="flex items-center justify-between text-xs font-bold text-amber-800 mb-1">
              <span className="font-mono">P-000114</span>
              <span className="bg-amber-100 border border-amber-300 text-amber-800 px-1.5 py-0.2 rounded text-[10px]">Elevated Workload</span>
            </div>
            <p className="text-[11px] text-saathi-textMuted">
              High continuous duty days combined with recent deployment movement.
            </p>
          </div>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        <div className="p-4 rounded-lg bg-white border border-saathi-border shadow-gov">
          <span className="text-[11px] font-bold text-saathi-textMuted uppercase tracking-wider">Total Monitored</span>
          <div className="text-2xl font-black text-saathi-textDark mt-1">1,470</div>
          <span className="text-[10px] text-saathi-textSubtle">Pseudonymous Roster</span>
        </div>

        <div className="p-4 rounded-lg bg-white border border-emerald-300 shadow-gov">
          <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider">🟢 GREEN (Stable)</span>
          <div className="text-2xl font-black text-emerald-700 mt-1">{getKpiCount('GREEN') || '1,120'}</div>
          <span className="text-[10px] text-saathi-textMuted">Normal Rhythm (&lt;30)</span>
        </div>

        <div className="p-4 rounded-lg bg-white border border-amber-300 shadow-gov">
          <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wider">🟡 YELLOW (Early)</span>
          <div className="text-2xl font-black text-amber-700 mt-1">{getKpiCount('YELLOW') || '207'}</div>
          <span className="text-[10px] text-saathi-textMuted">Mild Shift Surge (30-55)</span>
        </div>

        <div className="p-4 rounded-lg bg-white border border-orange-300 shadow-gov">
          <span className="text-[11px] font-bold text-orange-800 uppercase tracking-wider">🟠 ORANGE (Elevated)</span>
          <div className="text-2xl font-black text-orange-700 mt-1">{getKpiCount('ORANGE') || '98'}</div>
          <span className="text-[10px] text-saathi-textMuted">Check-in Advised (55-75)</span>
        </div>

        <div className="p-4 rounded-lg bg-white border border-red-300 shadow-gov">
          <span className="text-[11px] font-bold text-red-800 uppercase tracking-wider">🔴 RED (Priority Review)</span>
          <div className="text-2xl font-black text-red-700 mt-1">{getKpiCount('RED') || '45'}</div>
          <span className="text-[10px] text-saathi-textMuted">Action Plan (≥75)</span>
        </div>
      </div>

      {/* Main Triage Section */}
      <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov space-y-4">
        
        {/* Filter Bar */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-saathi-textMuted absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by pseudonymous ID (e.g. P-000013) or department..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded border border-saathi-border text-xs text-saathi-textDark bg-saathi-bg focus:bg-white focus:outline-none focus:border-saathi-primary font-medium"
            />
          </div>

          {/* Tier Filters */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {['ALL', 'RED', 'ORANGE', 'YELLOW', 'GREEN'].map((filter) => (
              <button
                key={filter}
                onClick={() => setSelectedFilter(filter)}
                className={`px-3 py-1.5 rounded text-xs font-bold transition-all border ${
                  selectedFilter === filter
                    ? 'bg-saathi-primary text-white border-saathi-primary shadow-xs'
                    : 'bg-saathi-bg border-saathi-border text-saathi-textMuted hover:border-saathi-primary'
                }`}
              >
                {filter}
              </button>
            ))}

            <button
              onClick={loadDashboardData}
              title="Refresh Triage"
              className="p-2 rounded bg-saathi-bg hover:bg-saathi-primarySubtle border border-saathi-border text-saathi-primary transition-colors ml-1"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto rounded border border-saathi-border">
          <table className="w-full text-left text-xs">
            <thead className="bg-saathi-bgAlt text-saathi-primary font-bold uppercase tracking-wider text-[10px] border-b border-saathi-border">
              <tr>
                <th className="py-2.5 px-4">Personnel ID</th>
                <th className="py-2.5 px-4">Support Score</th>
                <th className="py-2.5 px-4">Priority Tier</th>
                <th className="py-2.5 px-4">Prediction Reliability</th>
                <th className="py-2.5 px-4">Data Completeness</th>
                <th className="py-2.5 px-4">Review Status</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-saathi-borderLight text-saathi-textDark bg-white">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-saathi-textMuted">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-saathi-primary" />
                    Loading prioritized personnel roster...
                  </td>
                </tr>
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-saathi-textMuted">
                    No personnel match the selected filters.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => (
                  <tr
                    key={item.personnel_id}
                    onClick={() => navigate(`/personnel/${item.personnel_id}`)}
                    className="gov-table-row cursor-pointer group"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-saathi-textDark flex items-center gap-2">
                      <span>{item.personnel_id}</span>
                      {item.human_review_required && (
                        <span title="Human review recommended" className="w-2 h-2 rounded-full bg-red-600" />
                      )}
                    </td>

                    <td className="py-3 px-4 font-bold">
                      <span className="font-mono text-sm text-saathi-textDark">{item.support_score.toFixed(1)}</span>
                      <span className="text-[10px] text-saathi-textMuted"> / 100</span>
                    </td>

                    <td className="py-3 px-4">
                      <PriorityBadge priority={item.priority} size="sm" />
                    </td>

                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-[11px]">{(item.prediction_reliability * 100).toFixed(0)}%</span>
                        <div className="w-16 bg-saathi-bgAlt h-1.5 rounded-full overflow-hidden border border-saathi-border">
                          <div
                            className="bg-saathi-primary h-full rounded-full"
                            style={{ width: `${item.prediction_reliability * 100}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-[11px]">{(item.data_completeness * 100).toFixed(0)}%</span>
                        <div className="w-16 bg-saathi-bgAlt h-1.5 rounded-full overflow-hidden border border-saathi-border">
                          <div
                            className={`h-full rounded-full ${item.data_completeness >= 0.70 ? 'bg-emerald-600' : 'bg-amber-500'}`}
                            style={{ width: `${item.data_completeness * 100}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    <td className="py-3 px-4">
                      {item.human_review_required ? (
                        <span className="text-[10px] font-bold uppercase text-amber-900 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded">
                          Review Needed
                        </span>
                      ) : (
                        <span className="text-[10px] font-bold uppercase text-emerald-900 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded">
                          Monitoring
                        </span>
                      )}
                    </td>

                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/personnel/${item.personnel_id}`);
                        }}
                        className="text-xs font-bold text-saathi-primary hover:text-saathi-saffron group-hover:translate-x-0.5 transition-all inline-flex items-center gap-1"
                      >
                        <span>Inspect Profile</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

      </div>

    </div>
  );
};
