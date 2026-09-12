import { apiClient } from './client';
import { PersonnelSummary, HRProfile, PersonnelTimelineResponse } from '../types';

export const personnelApi = {
  listPersonnel: async (department?: string, limit = 100, offset = 0): Promise<PersonnelSummary[]> => {
    const params: Record<string, any> = { limit, offset };
    if (department) params.department = department;
    const res = await apiClient.get<PersonnelSummary[]>('/personnel/', { params });
    return res.data;
  },

  getProfile: async (personnelId: string): Promise<HRProfile> => {
    const res = await apiClient.get<HRProfile>(`/personnel/${personnelId}`);
    return res.data;
  },

  getTimeline: async (personnelId: string): Promise<PersonnelTimelineResponse> => {
    const res = await apiClient.get<PersonnelTimelineResponse>(`/personnel/${personnelId}/timeline`);
    return res.data;
  }
};
