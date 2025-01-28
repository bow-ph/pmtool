import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

// Base URL konfigurieren
const getBaseUrl = (): string => {
  try {
    const url = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    if (!/^https?:\/\//.test(url)) {
      throw new Error('Ungültiges URL-Schema. Die Base URL muss mit "http://" oder "https://" beginnen.');
    }
    return url.replace(/\/$/, ''); // Entferne abschließenden Slash
  } catch (error) {
    console.error('Fehler beim Abrufen der Base URL:', error.message || error);
    return 'http://localhost:8000'; // Fallback URL
  }
};

// Axios-Instanz erstellen
export const apiClient = axios.create({
  baseURL: `${getBaseUrl()}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Logging für Anfragen und Antworten
apiClient.interceptors.request.use(
  (request) => {
    console.log('API Request:', {
      url: request.url,
      method: request.method,
      data: request.data,
      headers: request.headers,
    });
    return request;
  },
  (error) => {
    console.error('Fehler beim Senden der Anfrage:', error.message);
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      url: response.config.url,
      status: response.status,
      data: response.data,
    });
    return response;
  },
  (error) => {
    console.error('API Fehler:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
    });
    if (error.response?.status === 401) {
      console.warn('Benutzer ist nicht autorisiert. Weiterleitung zur Anmeldung...');
      // Hier könnte man eine Weiterleitung zur Login-Seite einbauen
    }
    return Promise.reject(error);
  }
);

// React Query Client konfigurieren
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2, // Versuche Anfragen 2 Mal neu
      staleTime: 5 * 60 * 1000, // 5 Minuten
      onError: (error) => {
        console.error('Query Fehler:', error);
      },
    },
    mutations: {
      onError: (error) => {
        console.error('Mutationsfehler:', error);
      },
    },
  },
});

// API-Endpunkte definieren
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
