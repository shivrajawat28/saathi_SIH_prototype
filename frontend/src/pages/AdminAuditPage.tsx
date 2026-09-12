import React, { useState, useEffect } from 'react';
import { History, Shield, Lock, Search, Filter, RefreshCw, UserCheck, PlusCircle } from 'lucide-react';
import { auditApi } from '../api/audit';
import { authApi } from '../api/auth';
import { AuditLogEntry } from '../types';

export const AdminAuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionFilter, setActionFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const [showCreateUserModal, setShowCreateUserModal] = useState<boolean>(false);
  const [newUsername, setNewUsername] = useState<string>('');
  const [newEmail, setNewEmail] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');
  const [newFullName, setNewFullName] = useState<string>('');
  const [newRole, setNewRole] = useState<string>('WELFARE_OFFICER');
  const [userCreatedMsg, setUserCreatedMsg] = useState<string | null>(null);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const res = await auditApi.getLogs(100, 0, actionFilter || undefined, searchQuery || undefined);
      setLogs(res);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [actionFilter]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await authApi.createUser({
        username: newUsername,
        email: newEmail,
        password: newPassword,
        full_name: newFullName,
        role: newRole
      });
      setUserCreatedMsg(`User '${newUsername}' registered successfully as ${newRole}.`);
      setNewUsername('');
      setNewEmail('');
      setNewPassword('');
      setNewFullName('');
      setTimeout(() => {
        setShowCreateUserModal(false);
        setUserCreatedMsg(null);
        loadLogs();
      }, 1500);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create user.');
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-5 max-w-7xl mx-auto">
      
      {/* Header */}
      <div className="bg-white border-2 border-saathi-primary p-5 rounded-lg shadow-gov flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1 rounded bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
              <Shield className="w-4 h-4" />
            </span>
            <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-primary">
              System Administration & Security
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-saathi-textDark">
            Security, Access & Compliance Audit Trail
          </h1>
          <p className="text-xs text-saathi-textMuted mt-0.5 max-w-2xl">
            Immutable chronological logging of all sensitive operations, personnel inspections, predictions, and welfare interventions.
          </p>
        </div>

        <button
          onClick={() => setShowCreateUserModal(true)}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded bg-saathi-primary hover:bg-saathi-primaryLight text-white font-bold text-xs shadow-xs transition-colors self-start sm:self-auto cursor-pointer uppercase tracking-wider"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Provision User</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-white p-3.5 rounded-lg border border-saathi-border shadow-gov">
        <div className="flex items-center gap-2 flex-1 max-w-md">
          <Search className="w-4 h-4 text-saathi-textMuted" />
          <input
            type="text"
            placeholder="Search by actor username..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadLogs()}
            className="w-full bg-saathi-bg border border-saathi-border px-3 py-1.5 rounded text-xs text-saathi-textDark focus:bg-white focus:outline-none focus:border-saathi-primary font-medium"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-saathi-bg border border-saathi-border text-saathi-textDark text-xs px-3 py-1.5 rounded focus:bg-white focus:outline-none focus:border-saathi-primary font-medium"
          >
            <option value="">All Actions</option>
            <option value="VIEW_PERSONNEL_PROFILE">View Personnel Profile</option>
            <option value="VIEW_PERSONNEL_TIMELINE">View Timeline</option>
            <option value="RUN_PREDICTION">Run Prediction</option>
            <option value="CREATE_INTERVENTION">Create Intervention</option>
            <option value="RECORD_INTERVENTION_OUTCOME">Record Outcome</option>
            <option value="RUN_WHATIF_SIMULATION">Run What-If Simulation</option>
            <option value="SUBMIT_VOLUNTARY_WELLNESS">Submit Voluntary Wellness</option>
          </select>

          <button
            onClick={loadLogs}
            className="p-1.5 rounded bg-saathi-bg hover:bg-saathi-primarySubtle border border-saathi-border text-saathi-primary transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Logs Table */}
      <div className="p-5 sm:p-6 rounded-lg bg-white border border-saathi-border shadow-gov">
        <div className="overflow-x-auto rounded border border-saathi-border">
          <table className="w-full text-left text-xs">
            <thead className="bg-saathi-bgAlt text-saathi-primary font-bold uppercase tracking-wider text-[10px] border-b border-saathi-border">
              <tr>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Actor</th>
                <th className="py-2.5 px-4">Role</th>
                <th className="py-2.5 px-4">Action</th>
                <th className="py-2.5 px-4">Target Resource</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-saathi-borderLight text-saathi-textDark bg-white font-mono text-[11px]">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-saathi-textMuted font-sans text-xs">
                    Loading audit trail entries...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-saathi-textMuted font-sans text-xs">
                    No audit records match the selected filter.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="gov-table-row">
                    <td className="py-3 px-4 text-saathi-textMuted">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 font-bold text-saathi-textDark font-sans">{log.username}</td>
                    <td className="py-3 px-4 text-saathi-primary font-bold">{log.user_role}</td>
                    <td className="py-3 px-4 text-saathi-textDark font-semibold font-sans">{log.action}</td>
                    <td className="py-3 px-4 text-saathi-saffron font-bold">{log.target_resource}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.2 rounded text-[10px] font-bold ${
                        log.status === 'SUCCESS' 
                          ? 'bg-emerald-50 text-emerald-800 border border-emerald-300' 
                          : 'bg-red-50 text-red-800 border border-red-300'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-saathi-textMuted max-w-xs truncate font-sans text-[11px]" title={log.details}>
                      {log.details || '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create User Modal */}
      {showCreateUserModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-white border-2 border-saathi-primary w-full max-w-md rounded-lg p-5 shadow-gov-lg space-y-3.5">
            <h3 className="text-base font-bold text-saathi-textDark uppercase tracking-wider">Provision System User</h3>
            
            <form onSubmit={handleCreateUser} className="space-y-3 bg-saathi-bg p-4 rounded border border-saathi-border">
              <div>
                <label className="block text-xs text-saathi-textDark font-bold uppercase mb-1">Username</label>
                <input
                  type="text"
                  required
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  className="w-full px-3 py-1.5 rounded border border-saathi-border bg-white text-xs text-saathi-textDark"
                />
              </div>

              <div>
                <label className="block text-xs text-saathi-textDark font-bold uppercase mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  className="w-full px-3 py-1.5 rounded border border-saathi-border bg-white text-xs text-saathi-textDark"
                />
              </div>

              <div>
                <label className="block text-xs text-saathi-textDark font-bold uppercase mb-1">Full Name</label>
                <input
                  type="text"
                  value={newFullName}
                  onChange={(e) => setNewFullName(e.target.value)}
                  className="w-full px-3 py-1.5 rounded border border-saathi-border bg-white text-xs text-saathi-textDark"
                />
              </div>

              <div>
                <label className="block text-xs text-saathi-textDark font-bold uppercase mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-3 py-1.5 rounded border border-saathi-border bg-white text-xs text-saathi-textDark"
                />
              </div>

              <div>
                <label className="block text-xs text-saathi-textDark font-bold uppercase mb-1">Operational Role</label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  className="w-full px-3 py-1.5 rounded border border-saathi-border bg-white text-xs text-saathi-textDark"
                >
                  <option value="WELFARE_OFFICER">WELFARE_OFFICER</option>
                  <option value="COMMANDER">COMMANDER</option>
                  <option value="ANALYST">ANALYST</option>
                  <option value="PERSONNEL">PERSONNEL</option>
                  <option value="ADMIN">ADMIN</option>
                </select>
              </div>

              {userCreatedMsg && (
                <div className="p-2 rounded bg-emerald-50 border border-emerald-300 text-xs text-emerald-800 font-bold">
                  {userCreatedMsg}
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateUserModal(false)}
                  className="px-3 py-1.5 rounded bg-white border border-saathi-border text-xs text-saathi-textDark font-bold hover:bg-saathi-bg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded bg-saathi-primary text-xs text-white font-bold hover:bg-saathi-primaryLight shadow-xs"
                >
                  Create User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
