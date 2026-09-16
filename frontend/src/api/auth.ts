import { apiClient } from './client';
import { AuthResponse, UserProfile } from '../types';

export const authApi = {
  login: async (username: string, password: string): Promise<AuthResponse> => {
    try {
      const res = await apiClient.post<AuthResponse>('/auth/login', { username, password });
      return res.data;
    } catch (err: any) {
      // If transient 502/503/504 or network disconnect during server wake-up, attempt 1 recovery retry after 1.5s
      // NEVER retry 401, 400, 403, or 422
      const isTransient = (!err.response && (err.code === 'ERR_NETWORK' || err.message === 'Network Error')) ||
        (err.response && [502, 503, 504].includes(err.response.status));

      if (isTransient) {
        console.warn('Transient server wake-up / network issue detected. Attempting 1 automatic retry...');
        await new Promise(resolve => setTimeout(resolve, 1500));
        const retryRes = await apiClient.post<AuthResponse>('/auth/login', { username, password });
        return retryRes.data;
      }
      throw err;
    }
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
