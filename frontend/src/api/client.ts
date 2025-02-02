import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

// Create axios instance with default config

const getBaseUrl = () => {
  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }
  return window.location.protocol === 'https:' ? 'https://admin.docuplanai.com' : 'http://admin.docuplanai.com';
};

// Ensure we're using the correct API version prefix
const getApiUrl = (endpoint: string) => {
  if (!endpoint.startsWith('/api/v1/')) {
    return `/api/v1${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  }
  return endpoint;
};

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
      localStorage.removeItem('access_token');
      window.location.href = '/login';
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
  analyzePdf: (projectId: number, filename: string) => `/api/v1/projects/${projectId}/analyze-pdf/${encodeURIComponent(filename)}`,
  getAnalyzedTasks: (projectId: number) => `/api/v1/projects/${projectId}/tasks`,
  uploadPdf: (projectId: number) => `/api/v1/projects/${projectId}/upload-pdf`,
  getUploadedPdfs: (projectId: number) => `/api/v1/projects/${projectId}/uploaded-pdfs`,
  getTasks: (projectId?: number) => projectId ? `/api/v1/projects/${projectId}/tasks` : `/api/v1/todo/tasks`,
  getTasksByDate: (startDate: string, endDate: string) => `/api/v1/todo/tasks?start_date=${startDate}&end_date=${endDate}`,
  getTask: (taskId: number) => `/api/v1/todo/tasks/${taskId}`,
  updateTask: (taskId: number) => `/api/v1/todo/tasks/${taskId}`,
  deleteTask: (taskId: number) => `/api/v1/todo/tasks/${taskId}`,
  createTask: () => `/api/v1/todo/tasks`,
  getDashboardTasks: () => `/api/v1/todo/tasks`,
  moveTaskToDashboard: (taskId: number) => `/api/v1/todo/tasks/${taskId}/move-to-dashboard`,
  getPackages: () => 'packages',
  getSubscriptions: () => 'admin/subscriptions',
  getInvoices: () => 'admin/invoices',
  // User subscription endpoints
  // Auth endpoints
  login: () => getApiUrl('/auth/login'),
  register: () => getApiUrl('/auth/register'),
  resetPassword: (email: string) => getApiUrl(`/auth/reset-password/${email}`),
  testToken: () => getApiUrl('/auth/test-token'),
  
  // Subscription endpoints
  getMySubscription: () => '/api/v1/subscriptions/me',
  checkProjectLimit: () => '/api/v1/subscriptions/me/project-limit',
  cancelSubscription: () => '/api/v1/subscriptions/me/cancel',
};
