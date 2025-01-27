import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

// Create axios instance with default config
const getBaseUrl = () => {
  try {
    return import.meta.env.VITE_API_URL;
  } catch {
    // For test environment
    return 'http://localhost:8000';
  }
};

export const apiClient = axios.create({
  baseURL: getBaseUrl() || 'http://admin.docuplanai.com',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Origin': 'http://docuplanai.com'
  },
  withCredentials: true,
  validateStatus: (status) => {
    return status >= 200 && status < 500;
  }
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
  getMySubscription: () => `/subscriptions/me`,
  checkProjectLimit: () => `/subscriptions/me/project-limit`,
  cancelSubscription: () => `/subscriptions/me/cancel`,
  getTasks: (projectId: number, startDate: string, endDate: string) => 
    `/api/v1/todo/list?project_id=${projectId}&start_date=${startDate}&end_date=${endDate}`,
  updateTask: (taskId: number) => `/api/v1/todo/tasks/${taskId}`,
  getCalendarTasks: (projectId: number, startDate: string, endDate: string) =>
    `/api/v1/caldav/tasks/${projectId}/PM%20Tool?start_date=${startDate}&end_date=${endDate}`,
  packages: () => `/api/v1/packages`,
  createPackage: () => `/api/v1/packages`,
  updatePackage: (packageId: number) => `/api/v1/packages/${packageId}`,
  deletePackage: (packageId: number) => `/api/v1/packages/${packageId}`,
};
