import { apiClient } from './client';
import { InterventionCreate, InterventionResponse, OutcomeCreate, OutcomeResponse } from '../types';

export const interventionsApi = {
  createIntervention: async (data: InterventionCreate): Promise<InterventionResponse> => {
    const res = await apiClient.post<InterventionResponse>('/interventions/', data);
    return res.data;
  },

  getInterventionsForPersonnel: async (personnelId: string): Promise<InterventionResponse[]> => {
    const res = await apiClient.get<InterventionResponse[]>(`/interventions/personnel/${personnelId}`);
    return res.data;
  },

  recordOutcome: async (interventionId: string, outcomeData: OutcomeCreate): Promise<OutcomeResponse> => {
    const res = await apiClient.post<OutcomeResponse>(`/interventions/${interventionId}/outcomes`, outcomeData);
    return res.data;
  }
};
