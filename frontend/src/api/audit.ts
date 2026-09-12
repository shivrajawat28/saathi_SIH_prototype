import { apiClient } from './client';
import { AuditLogEntry } from '../types';

export const auditApi = {
  getLogs: async (limit = 100, offset = 0, action?: string, username?: string): Promise<AuditLogEntry[]> => {
    const params: Record<string, any> = { limit, offset };
    if (action) params.action = action;
    if (username) params.username = username;
    const res = await apiClient.get<AuditLogEntry[]>('/audit/logs', { params });
    return res.data;
  }
};
