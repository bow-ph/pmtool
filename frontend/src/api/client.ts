import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

// Create axios instance with default config

export const apiClient = axios.create({
  baseURL: 'https://admin.docuplanai.com/api/v1',
  headers: {
    'Content-Type': 'application/json'
  },
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
  analyzePdf: (projectId: number) => `/projects/${projectId}/analyze-pdf`,
  uploadPdf: (projectId: number) => `/projects/${projectId}/upload-pdf`,
  getUploadedPdfs: (projectId: number) => `/projects/${projectId}/uploaded-pdfs`,
  getProactiveHints: (projectId: number) => `/projects/${projectId}/proactive-hints`,
  getTasks: () => '/tasks',
  getTask: (taskId: number) => `/tasks/${taskId}`,
  createTask: () => '/tasks',
  updateTask: (taskId: number) => `/tasks/${taskId}`,
  deleteTask: (taskId: number) => `/tasks/${taskId}`,
  getPackages: () => '/packages',
  getSubscriptions: () => '/admin/subscriptions',
  getInvoices: () => '/admin/invoices',
  // User subscription endpoints
  getMySubscription: () => '/subscriptions/me',
  checkProjectLimit: () => '/subscriptions/me/project-limit',
  cancelSubscription: () => '/subscriptions/me/cancel',
};
