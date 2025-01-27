import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

// Create axios instance with default config
// Temporary test change for verifying PR workflow
const getBaseUrl = () => {
  try {
    return import.meta.env.VITE_API_URL;
  } catch {
    // For test environment
    return 'http://localhost:8000';
  }
};

export const apiClient = axios.create({
  baseURL: (getBaseUrl() || 'https://admin.docuplanai.com') + '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  },
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
  getProactiveHints: (projectId: number) => `/projects/${projectId}/proactive-hints`,
  getTasks: () => '/tasks',
  getTask: (taskId: number) => `/tasks/${taskId}`,
  createTask: () => '/tasks',
  updateTask: (taskId: number) => `/tasks/${taskId}`,
  deleteTask: (taskId: number) => `/tasks/${taskId}`,
  getPackages: () => '/packages',
  getSubscriptions: () => '/admin/subscriptions',
  getInvoices: () => '/admin/invoices',
};
