import React from 'react';
import { format, startOfWeek, addDays, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns';
import { de } from 'date-fns/locale';

interface CalendarEvent {
  id: string;
  title: string;
  date: Date;
  type: 'task' | 'meeting' | 'deadline';
}

interface CalendarViewProps {
  events: CalendarEvent[];
}

const CalendarView: React.FC<CalendarViewProps> = ({ events }) => {
  const today = new Date();
  const monthStart = startOfMonth(today);
  const monthEnd = endOfMonth(today);
  const startDate = startOfWeek(monthStart, { locale: de });

  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const weekDays = Array.from(Array(7)).map((_, index) => {
    const day = addDays(startDate, index);
    return format(day, 'EEE', { locale: de });
  });

  const getEventsForDay = (date: Date) => {
    return events.filter(event => 
      format(event.date, 'yyyy-MM-dd') === format(date, 'yyyy-MM-dd')
    );
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          {format(today, 'MMMM yyyy', { locale: de })}
        </h2>
      </div>
      <div className="grid grid-cols-7 gap-px bg-gray-200">
        {weekDays.map((day) => (
          <div key={day} className="bg-gray-50 p-2 text-center text-sm font-medium text-gray-500">
            {day}
          </div>
        ))}
        {days.map((day) => {
          const dayEvents = getEventsForDay(day);
          return (
            <div
              key={day.toString()}
              className={`bg-white p-2 h-24 overflow-y-auto ${
                format(day, 'yyyy-MM-dd') === format(today, 'yyyy-MM-dd')
                  ? 'bg-blue-50'
                  : ''
              }`}
            >
              <div className="font-medium text-sm text-gray-900">
                {format(day, 'd')}
              </div>
              {dayEvents.map((event) => (
                <div
                  key={event.id}
                  className={`mt-1 px-2 py-1 text-xs rounded-md ${
                    event.type === 'task'
                      ? 'bg-blue-100 text-blue-800'
                      : event.type === 'meeting'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {event.title}
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CalendarView;
