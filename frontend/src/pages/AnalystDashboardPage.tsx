import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, ShieldCheck, Database, RefreshCw } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { analyticsApi } from '../api/analytics';
import { CommanderOverviewResponse } from '../types';

export const AnalystDashboardPage: React.FC = () => {
  const [overview, setOverview] = useState<CommanderOverviewResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const res = await analyticsApi.getCommanderOverview();
        setOverview(res);
      } catch (err) {
        console.error('Failed to load analyst data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="p-12 flex flex-col items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 text-saathi-primary animate-spin mb-3" />
        <span className="text-xs text-saathi-textMuted">Loading anonymized analytics & model metrics...</span>
      </div>
    );
  }

  const pieData = overview?.priority_distribution.map((item) => ({
    name: item.priority,
    value: item.count,
    color:
      item.priority === 'GREEN'
        ? '#15803d'
        : item.priority === 'YELLOW'
        ? '#d97706'
        : item.priority === 'ORANGE'
        ? '#c2410c'
        : '#b91c1c'
  })) || [];

  const deptData = overview?.department_breakdown || [];

  return (
    <div className="p-4 sm:p-6 space-y-5 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="bg-white border-2 border-saathi-primary p-5 rounded-lg shadow-gov flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1 rounded bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
              <BarChart3 className="w-4 h-4" />
            </span>
            <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-primary">
              Statistical Analytics & Telemetry Trends
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-saathi-textDark">
            Anonymized Welfare Analytics & Distribution
          </h1>
          <p className="text-xs text-saathi-textMuted mt-0.5 max-w-2xl">
            Statistical aggregation and division-level trends. Direct individual identity lookup is restricted.
          </p>
        </div>

        <div className="bg-saathi-bg border border-saathi-border p-3 rounded-lg flex items-center gap-3 shrink-0">
          <Database className="w-4 h-4 text-saathi-primary" />
          <div>
            <div className="text-xs font-bold text-saathi-textDark">Model Engine</div>
            <div className="text-[10px] text-saathi-textMuted">Random Forest + Platt Calibration</div>
          </div>
        </div>
      </div>

      {/* Grid of Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Pie Distribution */}
        <div className="lg:col-span-5 p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
          <h3 className="text-base font-bold text-saathi-textDark mb-0.5">Priority Classification Share</h3>
          <p className="text-xs text-saathi-textMuted mb-4">Distribution across total cohort (1,470 records)</p>
          
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: any) => [`${value} Personnel`, 'Count']}
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#d5dfd8', borderRadius: '0.5rem', fontSize: '11px', color: '#10231b' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Department Bar Distribution */}
        <div className="lg:col-span-7 p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
          <h3 className="text-base font-bold text-saathi-textDark mb-0.5">Operational Unit Support Distribution</h3>
          <p className="text-xs text-saathi-textMuted mb-4">Breakdown of support tiers across functional divisions</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#D5DFD8" opacity={0.7} />
                <XAxis dataKey="department" stroke="#4B6358" fontSize={10} tickLine={false} />
                <YAxis stroke="#4B6358" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#d5dfd8', borderRadius: '0.5rem', fontSize: '11px', color: '#10231b' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="green_count" name="GREEN" fill="#15803d" stackId="a" />
                <Bar dataKey="yellow_count" name="YELLOW" fill="#d97706" stackId="a" />
                <Bar dataKey="orange_count" name="ORANGE" fill="#c2410c" stackId="a" />
                <Bar dataKey="red_count" name="RED" fill="#b91c1c" stackId="a" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

    </div>
  );
};
