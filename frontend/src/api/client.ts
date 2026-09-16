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
  timeout: 60000,
});

// Classify API errors accurately to distinguish credentials vs network/wake-up issues
export function getApiErrorMessage(err: any, defaultMsg = 'Authentication failed. Please check credentials.'): string {
  if (!err) return defaultMsg;

  // 1. Explicit backend validation/rejection detail
  if (err.response?.data?.detail) {
    const detail = err.response.data.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d: any) => d.msg || d.message || JSON.stringify(d)).join(', ');
    }
  }

  // 2. HTTP status code specific messages
  const status = err.response?.status;
  if (status === 401) {
    return 'Invalid username or password.';
  }
  if (status === 403) {
    return 'User account is deactivated or unauthorized.';
  }
  if (status === 429) {
    return 'Too many attempts. Please wait a moment before trying again.';
  }
  if (status === 502 || status === 503 || status === 504) {
    return 'SAATHI service is temporarily unavailable (waking up). Please try again.';
  }
  if (status && status >= 500) {
    return 'SAATHI service is temporarily unavailable. Please try again.';
  }

  // 3. Timeout and network connectivity
  if (err.code === 'ECONNABORTED' || err.message?.toLowerCase().includes('timeout')) {
    return 'The service is waking up. Please retry in a moment.';
  }
  if (err.message === 'Network Error' || err.code === 'ERR_NETWORK' || !err.response) {
    return 'Unable to reach the SAATHI service. Please check your connection.';
  }

  return err.message || defaultMsg;
}

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
