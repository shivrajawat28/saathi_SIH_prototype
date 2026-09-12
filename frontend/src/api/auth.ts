import { apiClient } from './client';
import { AuthResponse, UserProfile } from '../types';

export const authApi = {
  login: async (username: string, password: string): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/auth/login', { username, password });
    return res.data;
  },
  
  getProfile: async (): Promise<UserProfile> => {
    const res = await apiClient.get<UserProfile>('/auth/me');
    return res.data;
  },

  createUser: async (userData: any): Promise<UserProfile> => {
    const res = await apiClient.post<UserProfile>('/auth/users', userData);
    return res.data;
  }
};
