import { apiClient } from './client';
import { PredictionResponse, BatchTriageItem } from '../types';

export const predictionsApi = {
  predictPersonnel: async (personnelId: string, operatingThreshold = 0.50): Promise<PredictionResponse> => {
    const res = await apiClient.post<PredictionResponse>(
      `/predictions/personnel/${personnelId}`,
      {},
      { params: { operating_threshold: operatingThreshold } }
    );
    return res.data;
  },

  getBatchTriage: async (limit = 100, priorityFilter?: string): Promise<BatchTriageItem[]> => {
    const params: Record<string, any> = { limit };
    if (priorityFilter) params.priority_filter = priorityFilter;
    const res = await apiClient.get<BatchTriageItem[]>('/predictions/batch-triage', { params });
    return res.data;
  }
};
