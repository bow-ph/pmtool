import axios from 'axios';

// Erstelle die Axios-Instanz für FastAPI
export const apiClient = axios.create({
    baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1', // FastAPI-URL
    timeout: 10000, // Timeout für Anfragen
    headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
    },
});

// Typdefinitionen für API-Daten
export interface CalDAVTask {
    uid: string;
    description: string;
    start_date: string; // ISO-Format
    end_date: string;   // ISO-Format
    estimated_hours?: number;
    status: 'pending' | 'in_progress' | 'completed';
    priority?: 'high' | 'medium' | 'low';
}

export interface Schedule {
    earliest_start: string; // ISO-Format
    latest_end: string;     // ISO-Format
    total_duration_days: number;
    schedule: Array<{
        description: string;
        date: string;
        start_time: string;
        end_time: string;
        hours: number;
    }>;
}

export interface ScheduleValidation {
    is_valid: boolean;
    conflicts: string[];
    warnings: string[];
}

// API-Endpunkte für FastAPI

/**
 * Ruft CalDAV-Aufgaben eines Projekts ab.
 * @param projectId - ID des Projekts
 * @param startDate - Startdatum für die Abfrage
 * @param endDate - Enddatum für die Abfrage
 */
export const fetchCalDAVTasks = async (
    projectId: number,
    startDate: string,
    endDate: string
): Promise<CalDAVTask[]> => {
    const response = await apiClient.get(`/caldav/tasks/${projectId}`, {
        params: { start_date: startDate, end_date: endDate },
    });
    return response.data.tasks;
};

/**
 * Ruft den Zeitplan eines Projekts ab.
 * @param projectId - ID des Projekts
 */
export const fetchSchedule = async (projectId: number): Promise<Schedule> => {
    const response = await apiClient.get(`/scheduling/projects/${projectId}/schedule`);
    return response.data;
};

/**
 * Validiert den Zeitplan eines Projekts.
 * @param projectId - ID des Projekts
 * @param schedule - Der zu validierende Zeitplan
 */
export const validateSchedule = async (
    projectId: number,
    schedule: Schedule['schedule']
): Promise<ScheduleValidation> => {
    const response = await apiClient.post(`/scheduling/projects/${projectId}/validate-schedule`, {
        schedule,
    });
    return response.data;
};

/**
 * Aktualisiert ein spezifisches To-Do-Element.
 * @param itemId - ID des To-Do-Elements
 * @param updates - Änderungen, die angewendet werden sollen
 */
export const updateTodoItem = async (
    itemId: number,
    updates: Partial<TodoItem>
): Promise<TodoItem> => {
    const response = await apiClient.patch(`/todos/${itemId}`, updates);
    return response.data;
};

/**
 * Erstellt ein neues Projekt.
 * @param name - Name des Projekts
 */
export const createProject = async (name: string): Promise<{ id: number; name: string }> => {
    const response = await apiClient.post(`/projects/`, { name });
    return response.data;
};