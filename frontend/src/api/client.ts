import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('docuquest_token');
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
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect if not already on auth page
      const currentPath = window.location.pathname;
      if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
        localStorage.removeItem('docuquest_token');
        localStorage.removeItem('docuquest_user');
        window.location.href = '/login';
      }
    }
    // Enhance network error message if backend is unreachable
    if (!error.response && error.message === 'Network Error') {
      error.userFriendlyMessage = 'Unable to connect to the processing service. Please verify backend connectivity and CORS configuration.';
    }
    return Promise.reject(error);
  }
);

