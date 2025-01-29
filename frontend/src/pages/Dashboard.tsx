import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import CalendarView from '../components/Calendar/CalendarView';
import TodoList from '../components/TodoList/TodoList';

import { Task } from '@/types/api';

const Dashboard = () => {
  const { data: tasks = [], error } = useQuery<Task[]>({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await apiClient.get('/tasks');
      const tasksData = response.data.map((task: any) => ({
        ...task,
        status: task.status || 'pending',
        confidence_score: task.confidence_score || 0.5,
      }));
      return tasksData;
    },
  });

  if (error) {
    console.error('Fehler beim Abrufen der Aufgaben:', error);
  }

  // Convert tasks to calendar events
  const calendarEvents = tasks.map((task) => {
    const now = new Date();
    const startDate = now;
    const endDate = new Date(now.getTime() + (task.estimated_hours || 0) * 60 * 60 * 1000);

    return {
      id: task.id?.toString() || 'temp',
      title: task.description,
      start_date: startDate,
      end_date: endDate,
      type: 'task' as const,
    };
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <CalendarView events={calendarEvents} />
        </div>
        <div>
          <TodoList tasks={tasks} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
