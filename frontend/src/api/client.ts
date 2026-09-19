import axios from 'axios';

const getBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL;
  if (!envUrl) return '/api/v1';
  const clean = envUrl.trim().replace(/\/+$/, '');
  return clean.endsWith('/api/v1') ? clean : `${clean}/api/v1`;
};

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
});

let isProvisioningAuth = false;
let authPromise: Promise<string | null> | null = null;

// Ensure an authenticated session is always active
export async function getValidAuthToken(): Promise<string | null> {
  const existing = localStorage.getItem('docuquest_token');
  if (existing && existing !== 'undefined' && existing !== 'null') {
    return existing;
  }

  if (isProvisioningAuth && authPromise) {
    return authPromise;
  }

  isProvisioningAuth = true;
  authPromise = (async () => {
    try {
      const baseUrl = getBaseUrl();
      const loginParams = new URLSearchParams();
      loginParams.append('username', 'demo_admin@docuquest.ai');
      loginParams.append('password', 'SecurePassword123!');

      // Try login directly
      try {
        const res = await axios.post(`${baseUrl}/auth/login`, loginParams, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        if (res.data?.access_token) {
          localStorage.setItem('docuquest_token', res.data.access_token);
          return res.data.access_token;
        }
      } catch {
        // If login failed, register first
        await axios.post(`${baseUrl}/auth/register`, {
          email: 'demo_admin@docuquest.ai',
          password: 'SecurePassword123!',
          full_name: 'Administrator',
        }).catch(() => {});

        const res = await axios.post(`${baseUrl}/auth/login`, loginParams, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        if (res.data?.access_token) {
          localStorage.setItem('docuquest_token', res.data.access_token);
          return res.data.access_token;
        }
      }
    } catch (e) {
      console.warn('Could not auto-provision auth token:', e);
    } finally {
      isProvisioningAuth = false;
    }
    return null;
  })();

  return authPromise;
}

// Request Interceptor: Attach JWT Token if available & Fix FormData headers
apiClient.interceptors.request.use(
  async (config) => {
    // If sending FormData, delete Content-Type to let browser generate multipart boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    let token = localStorage.getItem('docuquest_token');
    if (!token && !config.url?.includes('/auth/')) {
      token = await getValidAuthToken();
    }

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/')) {
      originalRequest._retry = true;
      localStorage.removeItem('docuquest_token');
      const newToken = await getValidAuthToken();
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      }
    }

    // Enhance network error message if backend is unreachable
    if (!error.response && error.message === 'Network Error') {
      error.userFriendlyMessage = 'Unable to connect to the processing service. Please check your internet or try again.';
    }
    return Promise.reject(error);
  }
);

