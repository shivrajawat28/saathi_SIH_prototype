import { apiClient } from './client';
import { CommanderOverviewResponse } from '../types';

export const analyticsApi = {
  getCommanderOverview: async (): Promise<CommanderOverviewResponse> => {
    const res = await apiClient.get<CommanderOverviewResponse>('/analytics/commander-overview');
    return res.data;
  }
};
