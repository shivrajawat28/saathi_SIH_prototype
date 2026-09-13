import axios from 'axios';

const rawEnvBase = (import.meta.env.VITE_API_URL || '').trim().replace(/\/+$/, '');
const envBase = rawEnvBase && !rawEnvBase.startsWith('http://') && !rawEnvBase.startsWith('https://')
  ? `https://${rawEnvBase}`
  : rawEnvBase;
export const API_BASE_URL = envBase ? `${envBase}/api/v1` : '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Attach JWT Bearer Token to outgoing requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('saathi_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Handle global response errors (e.g. 401 Unauthorized)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and emit logout event if session expired
      if (window.location.pathname !== '/login') {
        localStorage.removeItem('saathi_token');
        localStorage.removeItem('saathi_user');
        window.location.href = '/login?session_expired=true';
      }
    }
    return Promise.reject(error);
  }
);
