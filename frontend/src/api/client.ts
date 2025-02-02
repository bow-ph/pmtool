import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

// Create axios instance with default config

const getBaseUrl = () => {
  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }
  return 'https://admin.docuplanai.com';
};

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests if it exists
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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
  login: () => '/api/v1/auth/login',
  register: () => '/api/v1/auth/register',
  resetPassword: (email: string) => `/api/v1/auth/reset-password/${email}`,
  testToken: () => '/api/v1/auth/test-token',
  
  // Subscription endpoints
  getMySubscription: () => '/api/v1/subscriptions/me',
  checkProjectLimit: () => '/api/v1/subscriptions/me/project-limit',
  cancelSubscription: () => '/api/v1/subscriptions/me/cancel',
};
