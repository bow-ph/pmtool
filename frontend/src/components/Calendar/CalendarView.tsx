import React, { useState, useEffect } from 'react';
import {
  format,
  startOfWeek,
  addDays,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isWithinInterval,
  parseISO,
} from 'date-fns';
import { de } from 'date-fns/locale';
import { useQuery } from '@tanstack/react-query';
import { CalDAVTask } from '../../types/api';
import { apiClient } from '../../api/client';

interface CalendarEvent {
  id: string;
  title: string;
  start_date: Date;
  end_date: Date;
  type: 'task' | 'meeting' | 'deadline';
  estimated_hours?: number;
  status?: 'pending' | 'in_progress' | 'completed';
  priority?: 'high' | 'medium' | 'low';
}

interface CalendarViewProps {
  projectId: number; // Dynamische Projekt-ID für API-Aufrufe
  events: CalendarEvent[];
  onEventUpdate?: (eventId: string, updates: Partial<CalendarEvent>) => void;
}

const CalendarView: React.FC<CalendarViewProps> = ({ projectId, events, onEventUpdate }) => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const monthStart = startOfMonth(selectedDate);
  const monthEnd = endOfMonth(selectedDate);
  const startDate = startOfWeek(monthStart, { locale: de });

  const days = eachDayOfInterval({ start: startDate, end: addDays(startDate, 6) });

  const weekDays = days.map((day) => format(day, 'EEE', { locale: de }));

  // Fetch calendar data from CalDAV
  const { data: calendarData, isLoading, isError } = useQuery({
    queryKey: ['calendar', projectId, monthStart.toISOString(), monthEnd.toISOString()],
    queryFn: async () => {
      const response = await apiClient.get(`/caldav/tasks/${projectId}`, {
        params: {
          start_date: monthStart.toISOString(),
          end_date: monthEnd.toISOString(),
        },
      });
      return response.data;
    },
    enabled: !!projectId,
  });

  // State for merged events and sync status
  const [mergedEvents, setMergedEvents] = useState<CalendarEvent[]>(events);

  useEffect(() => {
    if (calendarData?.tasks) {
      try {
        const externalEvents: CalendarEvent[] = calendarData.tasks.map((task: CalDAVTask) => ({
          id: task.uid,
          title: task.description,
          start_date: parseISO(task.start_date),
          end_date: parseISO(task.end_date),
          type: 'task',
          estimated_hours: task.estimated_hours,
          status: task.status as 'pending' | 'in_progress' | 'completed',
          priority: task.priority as 'high' | 'medium' | 'low',
        }));

        const merged = [...events];
        externalEvents.forEach((extEvent) => {
          const existingIndex = merged.findIndex((e) => e.id === extEvent.id);
          if (existingIndex >= 0) {
            merged[existingIndex] = { ...merged[existingIndex], ...extEvent };
          } else {
            merged.push(extEvent);
          }
        });

        setMergedEvents(merged);
      } catch (error) {
        console.error('Error syncing calendar:', error);
      }
    }
  }, [calendarData, events]);

  const getEventsForDay = (date: Date) => {
    return mergedEvents.filter((event) =>
      isWithinInterval(date, { start: event.start_date, end: event.end_date })
    );
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="p-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">
            {format(selectedDate, 'MMMM yyyy', { locale: de })}
          </h2>
          <div aria-live="polite">
            {isLoading && <span>Synchronisiere...</span>}
            {isError && <span className="text-red-600">Sync-Fehler</span>}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-7 bg-gray-200">
        {weekDays.map((day) => (
          <div key={day} className="text-center">
            {day}
          </div>
        ))}
        {days.map((day) => {
          const dayEvents = getEventsForDay(day);
          return (
            <div
              key={day.toISOString()}
              className={`p-2 bg-white ${dayEvents.length === 0 ? 'opacity-50' : ''
                }`}
            >
              <div className="font-medium">{format(day, 'd')}</div>
              {dayEvents.length > 0 ? (
                dayEvents.map((event) => (
                  <div key={event.id} className="text-sm text-gray-700">
                    {event.title}
                  </div>
                ))
              ) : (
                <span className="text-xs text-gray-500">Keine Events</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CalendarView;
