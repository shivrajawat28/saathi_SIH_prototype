import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Lock,
  RefreshCw,
  Clock,
  Send,
  AlertCircle,
  CheckCircle2,
  Calendar,
  UserCheck,
  Search,
  Filter,
  Eye,
  X
} from 'lucide-react';
import { analyticsApi } from '../api/analytics';
import { commanderApi } from '../api/commander';
import {
  CommanderOverviewResponse,
  PendingCheckInsSummary,
  PendingCheckInItem
} from '../types';

export const CommanderDashboardPage: React.FC = () => {
  const [overview, setOverview] = useState<CommanderOverviewResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Pending Check-ins State
  const [pendingSummary, setPendingSummary] = useState<PendingCheckInsSummary | null>(null);
  const [pendingLoading, setPendingLoading] = useState<boolean>(true);
  const [unitFilter, setUnitFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [page, setPage] = useState<number>(1);

  // Selected Personnel for Follow-up Details Modal
  const [selectedPersonnel, setSelectedPersonnel] = useState<PendingCheckInItem | null>(null);
  const [followUpNotes, setFollowUpNotes] = useState<string>('');
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await analyticsApi.getCommanderOverview();
      setOverview(res);
    } catch (err) {
      console.error('Failed to load commander overview:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadPendingCheckIns = async () => {
    setPendingLoading(true);
    try {
      const res = await commanderApi.getPendingCheckIns({
        unit: unitFilter || undefined,
        follow_up_status: statusFilter || undefined,
        search: searchQuery || undefined,
        page,
        page_size: 10
      });
      setPendingSummary(res);
    } catch (err) {
      console.error('Failed to load pending check-ins:', err);
    } finally {
      setPendingLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadPendingCheckIns();
  }, [unitFilter, statusFilter, searchQuery, page]);

  const handleOpenDetails = (item: PendingCheckInItem) => {
    setSelectedPersonnel(item);
    setFollowUpNotes('');
    setActionSuccess(null);
    setActionError(null);
  };

  const handleSendFollowUp = async (personnelId: string, notes?: string) => {
    setActionLoading(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      const res = await commanderApi.requestFollowUp(personnelId, {
        notes: notes || followUpNotes || undefined
      });
      setActionSuccess(`Check-in follow-up request registered for ${personnelId}.`);
      
      // Update local state
      if (selectedPersonnel && selectedPersonnel.personnel_id === personnelId) {
        setSelectedPersonnel({
          ...selectedPersonnel,
          follow_up_status: 'REQUESTED',
          last_followup_at: res.requested_at,
          last_followup_by: res.requested_by_username
        });
      }
      
      // Refresh list
      loadPendingCheckIns();
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Failed to send follow-up request.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 flex flex-col items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 text-saathi-primary animate-spin mb-3" />
        <span className="text-xs text-saathi-textMuted">Loading unit readiness & aggregate welfare metrics...</span>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="bg-white border-2 border-saathi-primary p-5 rounded-lg shadow-gov flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1 rounded bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
              <ShieldAlert className="w-4 h-4" />
            </span>
            <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-primary">
              Unit Commander Operational View
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-saathi-textDark">
            Aggregated Unit Welfare & Readiness Overview
          </h1>
          <p className="text-xs text-saathi-textMuted mt-0.5 max-w-2xl">
            High-level distribution overview and administrative check-in follow-up designed for operational commanders. Subjective personal check-ins are strictly confidential and restricted.
          </p>
        </div>

        {/* Psychological Safety Notice */}
        <div className="bg-saathi-bg border border-saathi-border p-3 rounded-lg flex items-center gap-3 shrink-0">
          <div className="p-2 rounded bg-white text-emerald-800 border border-emerald-200">
            <Lock className="w-4 h-4 text-emerald-700" />
          </div>
          <div>
            <div className="text-xs font-bold text-saathi-textDark">Psychological Safety Guard</div>
            <div className="text-[10px] text-saathi-textMuted">Zero individual survey text exposed</div>
          </div>
        </div>
      </div>

      {/* SECTION 1: Monthly Check-In Follow-up (NEW FEATURE) */}
      <div className="bg-white border-2 border-saathi-secondaryLight rounded-lg shadow-gov p-5 sm:p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-saathi-border pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-amber-100 text-amber-900 border border-amber-300">
                Administrative Follow-up
              </span>
              <span className="text-xs font-bold text-saathi-primary">
                Cycle: {pendingSummary?.cycle_label || 'Current Month'}
              </span>
            </div>
            <h2 className="text-lg font-black text-saathi-textDark flex items-center gap-2">
              <Clock className="w-5 h-5 text-amber-600" />
              Monthly Check-In Follow-up
            </h2>
            <p className="text-xs text-saathi-textMuted mt-0.5 max-w-3xl">
              Track personnel who have not submitted their expected monthly check-in for the current cycle. Initiate administrative follow-up reminders to support unit welfare participation without accessing confidential self-assessments.
            </p>
          </div>

          <button
            onClick={loadPendingCheckIns}
            disabled={pendingLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-saathi-bg hover:bg-saathi-bgAlt border border-saathi-border rounded text-xs font-bold text-saathi-textDark transition self-start sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${pendingLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Summary Metric Badges */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
          <div className="p-3.5 rounded-lg bg-saathi-bg border border-saathi-border flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-saathi-textMuted">
                Monthly Check-In Pending
              </span>
              <div className="text-xl font-black text-saathi-textDark mt-0.5">
                {pendingSummary?.total_pending ?? 0}
              </div>
              <span className="text-[10px] text-saathi-textSubtle">Awaiting monthly submission</span>
            </div>
            <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-700">
              <Clock className="w-5 h-5" />
            </div>
          </div>

          <div className="p-3.5 rounded-lg bg-saathi-bg border border-saathi-border flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-orange-800">
                Follow-up Required (&gt;15 Days)
              </span>
              <div className="text-xl font-black text-orange-700 mt-0.5">
                {pendingSummary?.overdue_count ?? 0}
              </div>
              <span className="text-[10px] text-saathi-textMuted">Elapsed check-in window</span>
            </div>
            <div className="p-2.5 rounded-lg bg-orange-50 border border-orange-200 text-orange-700">
              <AlertCircle className="w-5 h-5" />
            </div>
          </div>

          <div className="p-3.5 rounded-lg bg-saathi-bg border border-saathi-border flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-saathi-primary">
                Follow-up Requested
              </span>
              <div className="text-xl font-black text-saathi-primary mt-0.5">
                {pendingSummary?.followed_up_count ?? 0}
              </div>
              <span className="text-[10px] text-saathi-textMuted">Reminder active</span>
            </div>
            <div className="p-2.5 rounded-lg bg-saathi-primarySubtle border border-saathi-secondaryLight text-saathi-primary">
              <UserCheck className="w-5 h-5" />
            </div>
          </div>
        </div>

        {/* Search & Filter Toolbar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-1">
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-saathi-textMuted" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                placeholder="Search ID or Name..."
                className="pl-8 pr-3 py-1.5 bg-saathi-bg border border-saathi-border rounded text-xs text-saathi-textDark placeholder:text-saathi-textMuted focus:outline-none focus:border-saathi-primary w-48"
              />
            </div>

            <div className="flex items-center gap-1.5 bg-saathi-bg border border-saathi-border px-2.5 py-1 rounded">
              <Filter className="w-3.5 h-3.5 text-saathi-textMuted" />
              <select
                value={unitFilter}
                onChange={(e) => {
                  setUnitFilter(e.target.value);
                  setPage(1);
                }}
                className="bg-transparent text-xs text-saathi-textDark font-medium focus:outline-none"
              >
                <option value="">All Units / Divisions</option>
                <option value="Operations">Operations</option>
                <option value="Border Security">Border Security</option>
                <option value="Rapid Action">Rapid Action</option>
                <option value="Special Operations">Special Operations</option>
                <option value="Logistics">Logistics</option>
                <option value="Signals & Comms">Signals & Comms</option>
              </select>
            </div>

            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="bg-saathi-bg border border-saathi-border px-2.5 py-1.5 rounded text-xs text-saathi-textDark font-medium focus:outline-none"
            >
              <option value="">All Follow-up Statuses</option>
              <option value="NONE">No Follow-up Yet</option>
              <option value="REQUESTED">Follow-up Requested</option>
            </select>
          </div>

          <div className="text-[11px] text-saathi-textMuted font-mono self-end sm:self-auto">
            Showing {pendingSummary?.items.length ?? 0} of {pendingSummary?.total_items ?? 0} pending
          </div>
        </div>

        {/* Pending Check-Ins Table */}
        <div className="overflow-x-auto rounded border border-saathi-border">
          <table className="w-full text-left text-xs">
            <thead className="bg-saathi-bgAlt text-saathi-primary font-bold uppercase tracking-wider text-[10px] border-b border-saathi-border">
              <tr>
                <th className="py-2.5 px-4">Personnel ID & Name</th>
                <th className="py-2.5 px-3">Unit</th>
                <th className="py-2.5 px-3">Role</th>
                <th className="py-2.5 px-3">Last Check-in</th>
                <th className="py-2.5 px-3">Expected Cycle</th>
                <th className="py-2.5 px-3">Days Overdue</th>
                <th className="py-2.5 px-3">Submission Status</th>
                <th className="py-2.5 px-3">Follow-up Status</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-saathi-borderLight text-saathi-textDark bg-white">
              {pendingLoading ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-saathi-textMuted">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-saathi-primary" />
                    Loading pending monthly check-ins...
                  </td>
                </tr>
              ) : pendingSummary?.items.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-saathi-textMuted">
                    <CheckCircle2 className="w-6 h-6 text-emerald-600 mx-auto mb-2" />
                    <div className="font-bold text-saathi-textDark">All Monthly Check-Ins Submitted</div>
                    <div className="text-[11px] mt-0.5">No personnel with pending check-in windows under this filter.</div>
                  </td>
                </tr>
              ) : (
                pendingSummary?.items.map((item) => (
                  <tr key={item.personnel_id} className="hover:bg-saathi-bg transition">
                    <td className="py-3 px-4">
                      <div className="font-black text-saathi-textDark font-mono">{item.personnel_id}</div>
                      <div className="text-[11px] text-saathi-textMuted font-medium">{item.display_name}</div>
                    </td>
                    <td className="py-3 px-3 font-semibold text-saathi-textDark">{item.unit}</td>
                    <td className="py-3 px-3 text-saathi-textMuted">{item.role}</td>
                    <td className="py-3 px-3 font-mono text-[11px]">
                      {item.last_checkin_date || (
                        <span className="text-amber-700 italic">No Prior Record</span>
                      )}
                    </td>
                    <td className="py-3 px-3 font-mono font-medium">{item.expected_checkin_month}</td>
                    <td className="py-3 px-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                        item.days_overdue > 20
                          ? 'bg-red-100 text-red-800 border border-red-200'
                          : item.days_overdue > 10
                          ? 'bg-amber-100 text-amber-800 border border-amber-200'
                          : 'bg-saathi-bg text-saathi-textDark border border-saathi-border'
                      }`}>
                        {item.days_overdue} days
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-orange-50 text-orange-800 border border-orange-200">
                        {item.submission_status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      {item.follow_up_status === 'REQUESTED' ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
                          <CheckCircle2 className="w-3 h-3" />
                          Follow-up Requested
                        </span>
                      ) : (
                        <span className="text-[11px] text-saathi-textMuted italic">
                          None
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleOpenDetails(item)}
                          className="px-2.5 py-1 bg-saathi-bg hover:bg-saathi-bgAlt border border-saathi-border rounded text-[11px] font-bold text-saathi-textDark transition inline-flex items-center gap-1"
                        >
                          <Eye className="w-3 h-3" />
                          View Details
                        </button>
                        {item.follow_up_status !== 'REQUESTED' && (
                          <button
                            onClick={() => handleSendFollowUp(item.personnel_id)}
                            className="px-2.5 py-1 bg-saathi-primary hover:bg-saathi-primaryDark text-white rounded text-[11px] font-bold transition inline-flex items-center gap-1 shadow-sm"
                          >
                            <Send className="w-3 h-3" />
                            Request Check-In
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Table Pagination */}
        {pendingSummary && pendingSummary.total_items > pendingSummary.page_size && (
          <div className="flex items-center justify-between pt-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 bg-saathi-bg border border-saathi-border rounded text-xs font-bold disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-xs text-saathi-textMuted font-mono">
              Page {page} of {Math.ceil(pendingSummary.total_items / pendingSummary.page_size)}
            </span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= Math.ceil(pendingSummary.total_items / pendingSummary.page_size)}
              className="px-3 py-1 bg-saathi-bg border border-saathi-border rounded text-xs font-bold disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Restricted Follow-up Details Modal */}
      {selectedPersonnel && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border-2 border-saathi-primary rounded-lg shadow-2xl max-w-lg w-full p-5 sm:p-6 space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-start justify-between border-b border-saathi-border pb-3">
              <div>
                <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
                  Restricted Follow-up View
                </span>
                <h3 className="text-lg font-black text-saathi-textDark mt-1">
                  Monthly Check-In Follow-up Details
                </h3>
              </div>
              <button
                onClick={() => setSelectedPersonnel(null)}
                className="p-1 rounded text-saathi-textMuted hover:text-saathi-textDark hover:bg-saathi-bg transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Privacy Compliance Banner */}
            <div className="bg-emerald-50 border border-emerald-200 p-3 rounded text-[11px] text-emerald-800 flex items-center gap-2">
              <Lock className="w-4 h-4 shrink-0 text-emerald-700" />
              <span>
                <strong>Privacy Protected:</strong> Confidential wellness scores, survey questions, and chatbot transcripts are strictly withheld from administrative views.
              </span>
            </div>

            {/* Personnel Attributes Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs bg-saathi-bg p-3.5 rounded-lg border border-saathi-border">
              <div>
                <span className="text-[10px] font-bold text-saathi-textMuted uppercase tracking-wider">Personnel ID</span>
                <div className="font-mono font-bold text-saathi-textDark">{selectedPersonnel.personnel_id}</div>
              </div>
              <div>
                <span className="text-[10px] font-bold text-saathi-textMuted uppercase tracking-wider">Display Name / Rank</span>
                <div className="font-bold text-saathi-textDark">{selectedPersonnel.display_name}</div>
              </div>
              <div>
                <span className="text-[10px] font-bold text-saathi-textMuted uppercase tracking-wider">Unit / Battalion</span>
                <div className="font-medium text-saathi-textDark">{selectedPersonnel.unit}</div>
              </div>
              <div>
                <span className="text-[10px] font-bold text-saathi-textMuted uppercase tracking-wider">Operational Role</span>
                <div className="font-medium text-saathi-textDark">{selectedPersonnel.role}</div>
              </div>
              <div>
                <span className="text-[10px] font-bold text-saathi-textMuted uppercase tracking-wider">Last Check-in</span>
                <div className="font-mono text-saathi-textDark">
                  {selectedPersonnel.last_checkin_date || 'No Prior Submission'}
                </div>
              </div>
              <div>
                <span className="text-[10px] font-bold text-saathi-textMuted uppercase tracking-wider">Expected Cycle</span>
                <div className="font-mono font-bold text-saathi-textDark">{selectedPersonnel.expected_checkin_month}</div>
              </div>
              <div>
                <span className="text-[10px] font-bold text-saathi-textMuted uppercase tracking-wider">Days Overdue</span>
                <div className="font-mono font-bold text-amber-700">{selectedPersonnel.days_overdue} days</div>
              </div>
              <div>
                <span className="text-[10px] font-bold text-saathi-textMuted uppercase tracking-wider">Submission Status</span>
                <div className="font-bold text-orange-700">{selectedPersonnel.submission_status.replace('_', ' ')}</div>
              </div>
            </div>

            {/* Follow-up Tracking Status */}
            <div className="p-3 bg-saathi-bgAlt border border-saathi-border rounded text-xs space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-saathi-textDark">Follow-up Status:</span>
                <span className={`font-mono font-bold px-2 py-0.5 rounded text-[10px] ${
                  selectedPersonnel.follow_up_status === 'REQUESTED'
                    ? 'bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight'
                    : 'bg-white text-saathi-textMuted border border-saathi-border'
                }`}>
                  {selectedPersonnel.follow_up_status === 'REQUESTED' ? 'FOLLOW-UP REQUESTED' : 'NO ACTION PENDING'}
                </span>
              </div>
              {selectedPersonnel.last_followup_at && (
                <div className="text-[11px] text-saathi-textMuted">
                  Last Requested: <span className="font-mono">{new Date(selectedPersonnel.last_followup_at).toLocaleString()}</span>
                  {selectedPersonnel.last_followup_by && ` by ${selectedPersonnel.last_followup_by}`}
                </div>
              )}
            </div>

            {/* Follow-up Note Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-saathi-textDark">
                Administrative Reminder Note (Optional)
              </label>
              <textarea
                value={followUpNotes}
                onChange={(e) => setFollowUpNotes(e.target.value)}
                placeholder="e.g., Monthly check-in window elapsed. Please submit check-in on personnel portal."
                rows={2}
                maxLength={300}
                className="w-full p-2.5 bg-saathi-bg border border-saathi-border rounded text-xs text-saathi-textDark focus:outline-none focus:border-saathi-primary"
              />
              <span className="text-[10px] text-saathi-textMuted">Max 300 characters. Visible to administrative audit log.</span>
            </div>

            {/* Feedback Alerts */}
            {actionSuccess && (
              <div className="p-3 rounded bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
                {actionSuccess}
              </div>
            )}
            {actionError && (
              <div className="p-3 rounded bg-red-50 border border-red-200 text-xs text-red-800 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
                {actionError}
              </div>
            )}

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-saathi-border">
              <button
                type="button"
                onClick={() => setSelectedPersonnel(null)}
                className="px-3.5 py-1.5 bg-saathi-bg hover:bg-saathi-bgAlt border border-saathi-border rounded text-xs font-bold text-saathi-textDark transition"
              >
                Close
              </button>
              <button
                type="button"
                onClick={() => handleSendFollowUp(selectedPersonnel.personnel_id)}
                disabled={actionLoading}
                className="px-4 py-1.5 bg-saathi-primary hover:bg-saathi-primaryDark text-white rounded text-xs font-bold transition flex items-center gap-1.5 shadow-md disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                {actionLoading ? 'Recording...' : 'Request Monthly Check-In'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* KPI Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div className="p-4 rounded-lg bg-white border border-saathi-border shadow-gov">
          <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-textMuted">Total Unit Strength</span>
          <div className="text-2xl font-black text-saathi-textDark mt-1">{overview?.total_strength ?? 1470}</div>
          <span className="text-[10px] text-saathi-textSubtle">Personnel on active roster</span>
        </div>

        <div className="p-4 rounded-lg bg-white border border-orange-300 shadow-gov">
          <span className="text-[11px] font-bold uppercase tracking-wider text-orange-800">Elevated Priority Total</span>
          <div className="text-2xl font-black text-orange-700 mt-1">{overview?.high_risk_total ?? 143}</div>
          <span className="text-[10px] text-saathi-textMuted">ORANGE + RED tiers</span>
        </div>

        <div className="p-4 rounded-lg bg-white border border-saathi-border shadow-gov">
          <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-primary">Active Welfare Actions</span>
          <div className="text-2xl font-black text-saathi-primary mt-1">{overview?.interventions_active_count ?? 12}</div>
          <span className="text-[10px] text-saathi-textMuted">Under officer review</span>
        </div>

        <div className="p-4 rounded-lg bg-white border border-emerald-300 shadow-gov">
          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-800">Resolved / Improved</span>
          <div className="text-2xl font-black text-emerald-700 mt-1">{overview?.interventions_improved_count ?? 8}</div>
          <span className="text-[10px] text-saathi-textMuted">Closed-loop recovery</span>
        </div>
      </div>

      {/* Priority Distribution Progress Bar */}
      <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
        <h3 className="text-base font-bold text-saathi-textDark mb-0.5">Unit Welfare Priority Tier Distribution</h3>
        <p className="text-xs text-saathi-textMuted mb-4">
          Distribution across 1,470 personnel categorized by continuous support priority score.
        </p>

        {/* Stacked Bar */}
        <div className="w-full h-5 rounded bg-saathi-bg overflow-hidden flex border border-saathi-border shadow-inner">
          {overview?.priority_distribution.map((item) => (
            <div
              key={item.priority}
              title={`${item.priority}: ${item.count} (${item.percentage}%)`}
              className={`h-full transition-all ${
                item.priority === 'GREEN'
                  ? 'bg-emerald-600'
                  : item.priority === 'YELLOW'
                  ? 'bg-amber-500'
                  : item.priority === 'ORANGE'
                  ? 'bg-orange-500'
                  : 'bg-red-600'
              }`}
              style={{ width: `${item.percentage}%` }}
            />
          ))}
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
          {overview?.priority_distribution.map((item) => (
            <div key={item.priority} className="p-3 rounded bg-saathi-bg border border-saathi-border">
              <div className="flex items-center gap-1.5 mb-1">
                <span className={`w-2.5 h-2.5 rounded-full ${
                  item.priority === 'GREEN'
                    ? 'bg-emerald-600'
                    : item.priority === 'YELLOW'
                    ? 'bg-amber-500'
                    : item.priority === 'ORANGE'
                    ? 'bg-orange-500'
                    : 'bg-red-600'
                }`} />
                <span className="text-xs font-bold text-saathi-textDark">{item.priority}</span>
              </div>
              <div className="text-xl font-black text-saathi-textDark font-mono">{item.count}</div>
              <div className="text-[11px] text-saathi-textMuted font-medium">{item.percentage}% of unit</div>
            </div>
          ))}
        </div>
      </div>

      {/* Unit / Functional Area Breakdown Table */}
      <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov space-y-3.5">
        <div className="flex items-center justify-between border-b border-saathi-border pb-2.5">
          <div>
            <h3 className="text-base font-bold text-saathi-textDark mb-0.5">Unit / Division Welfare Indicators</h3>
            <p className="text-xs text-saathi-textMuted">
              Aggregated distribution indicators by operational division. Individual telemetry remains confidential.
            </p>
          </div>
          <span className="text-[10px] font-mono font-bold text-saathi-textMuted bg-saathi-bg border border-saathi-border px-2 py-0.5 rounded">
            Synthetic Telemetry
          </span>
        </div>

        <div className="overflow-x-auto rounded border border-saathi-border">
          <table className="w-full text-left text-xs">
            <thead className="bg-saathi-bgAlt text-saathi-primary font-bold uppercase tracking-wider text-[10px] border-b border-saathi-border">
              <tr>
                <th className="py-2.5 px-4">Operational Unit / Division</th>
                <th className="py-2.5 px-4">Total Personnel</th>
                <th className="py-2.5 px-4">🟢 Stable</th>
                <th className="py-2.5 px-4">🟡 Early</th>
                <th className="py-2.5 px-4">🟠 Elevated</th>
                <th className="py-2.5 px-4">🔴 Priority</th>
                <th className="py-2.5 px-4 text-right">Avg Support Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-saathi-borderLight text-saathi-textDark bg-white">
              {overview?.department_breakdown.map((dept) => (
                <tr key={dept.department} className="gov-table-row">
                  <td className="py-3 px-4 font-bold text-saathi-textDark">{dept.department}</td>
                  <td className="py-3 px-4 font-mono font-medium">{dept.total_personnel}</td>
                  <td className="py-3 px-4 text-emerald-700 font-mono font-bold">{dept.green_count}</td>
                  <td className="py-3 px-4 text-amber-700 font-mono font-bold">{dept.yellow_count}</td>
                  <td className="py-3 px-4 text-orange-700 font-mono font-bold">{dept.orange_count}</td>
                  <td className="py-3 px-4 text-red-700 font-mono font-bold">{dept.red_count}</td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-saathi-primary">
                    {dept.avg_support_score.toFixed(1)} / 100
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
