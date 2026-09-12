import { apiClient } from './client';
import {
  PendingCheckInsSummary,
  PendingCheckInItem,
  CheckInFollowUpRequest,
  CheckInFollowUpResponse
} from '../types';

export const commanderApi = {
  getPendingCheckIns: async (params?: {
    unit?: string;
    role?: string;
    follow_up_status?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<PendingCheckInsSummary> => {
    const res = await apiClient.get<PendingCheckInsSummary>('/commander/pending-checkins', {
      params
    });
    return res.data;
  },

  getPendingPersonnelDetail: async (personnelId: string): Promise<PendingCheckInItem> => {
    const res = await apiClient.get<PendingCheckInItem>(`/commander/pending-checkins/${personnelId}`);
    return res.data;
  },

  requestFollowUp: async (
    personnelId: string,
    data?: CheckInFollowUpRequest
  ): Promise<CheckInFollowUpResponse> => {
    const res = await apiClient.post<CheckInFollowUpResponse>(
      `/commander/pending-checkins/${personnelId}/follow-up`,
      data || {}
    );
    return res.data;
  }
};
