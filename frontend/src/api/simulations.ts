import { apiClient } from './client';
import { SimulationRequest, SimulationResponse } from '../types';

export const simulationsApi = {
  runSimulation: async (personnelId: string, simulationData: SimulationRequest): Promise<SimulationResponse> => {
    const res = await apiClient.post<SimulationResponse>(`/simulations/personnel/${personnelId}`, simulationData);
    return res.data;
  }
};
