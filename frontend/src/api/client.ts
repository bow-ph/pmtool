import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

// Create axios instance with default config

const getBaseUrl = () => {
  if (import.meta.env.DEV) {
    return 'http://localhost:8000/api/v1';
  }
  return 'https://admin.docuplanai.com/api/v1';
};

// Configure axios defaults for production
const setupAxiosDefaults = () => {
  if (!import.meta.env.DEV) {
    apiClient.defaults.headers['Access-Control-Allow-Origin'] = 'https://docuplanai.com';
    apiClient.defaults.headers['Access-Control-Allow-Credentials'] = 'true';
  }
};</old_str>
<new_str>const getBaseUrl = () => {
  if (import.meta.env.DEV) {
    return 'http://localhost:8000/api/v1';
  }
  return 'https://admin.docuplanai.com/api/v1';
};

// Configure axios defaults for production
const setupAxiosDefaults = () => {
  if (!import.meta.env.DEV) {
    apiClient.defaults.headers['Access-Control-Allow-Origin'] = 'https://docuplanai.com';
    apiClient.defaults.headers['Access-Control-Allow-Credentials'] = 'true';
  }
};

setupAxiosDefaults();

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true,
  validateStatus: function (status) {
    return status >= 200 && status < 500;
  }
});

// Add auth token to requests if it exists and handle token refresh
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Clear the invalid token
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return Promise.reject(error);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// Create react-query client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// API endpoints
export const endpoints = {
  analyzePdf: (projectId: number, filename: string) => `/projects/${projectId}/analyze-pdf/${encodeURIComponent(filename)}`,
  getAnalyzedTasks: (projectId: number) => `/projects/${projectId}/tasks`,
  uploadPdf: (projectId: number) => `/projects/${projectId}/upload-pdf`,
  getUploadedPdfs: (projectId: number) => `/projects/${projectId}/uploaded-pdfs`,
  getTasks: (projectId?: number) => projectId ? `/projects/${projectId}/tasks` : `/todo/tasks`,
  getTasksByDate: (startDate: string, endDate: string) => `/todo/tasks?start_date=${startDate}&end_date=${endDate}`,
  getTask: (taskId: number) => `/todo/tasks/${taskId}`,
  updateTask: (taskId: number) => `/todo/tasks/${taskId}`,
  deleteTask: (taskId: number) => `/todo/tasks/${taskId}`,
  createTask: () => `/todo/tasks`,
  getDashboardTasks: () => `/todo/tasks`,
  moveTaskToDashboard: (taskId: number) => `/todo/tasks/${taskId}/move-to-dashboard`,
  getPackages: () => 'packages',
  getSubscriptions: () => 'admin/subscriptions',
  getInvoices: () => 'admin/invoices',
  // User subscription endpoints
  // Auth endpoints
  login: () => '/auth/login',
  register: () => '/auth/register',
  resetPassword: (email: string) => `/auth/reset-password/${email}`,
  testToken: () => '/auth/test-token',
  
  // Subscription endpoints
  getMySubscription: () => '/subscriptions/me',
  checkProjectLimit: () => '/subscriptions/me/project-limit',
  cancelSubscription: () => '/subscriptions/me/cancel',
};
