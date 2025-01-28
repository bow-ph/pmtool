import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

const getBaseUrl = () => {
  try {
    const url = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    return url.replace(/\/$/, ''); // Entfernt abschließenden Slash
  } catch (error) {
    console.error('Fehler beim Abrufen der Base URL:', error);
    return 'http://localhost:8000';
  }
};

export const apiClient = axios.create({
  baseURL: `${getBaseUrl()}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Logging für Anfragen und Antworten
apiClient.interceptors.request.use((request) => {
  console.log('API Request:', request);
  return request;
});

apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response || error.message);
    return Promise.reject(error);
  }
);

// React Query Client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 Minuten
      onError: (error) => {
        console.error('Query Error:', error);
      },
    },
  },
});

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
  getMySubscription: () => '/subscriptions/me',
  checkProjectLimit: () => '/subscriptions/me/project-limit',
  cancelSubscription: () => '/subscriptions/me/cancel',
};
};
