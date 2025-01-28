import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import CalendarView from '../components/Calendar/CalendarView';
import TodoList from '../components/TodoList/TodoList';
import { Task } from '../types/api';

const Dashboard = () => {
  const { data: tasks = [], error } = useQuery<Task[]>({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await apiClient.get('/tasks');
      return response.data;
    },
  });

  if (error) {
    console.error('Fehler beim Abrufen der Aufgaben:', error);
  }

  // Convert tasks to calendar events
  const calendarEvents = tasks.map((task) => ({
    id: task.id?.toString() || '',
    title: task.description,
    start_date: task.start_date ? new Date(task.start_date) : new Date(), // Sicherstellen, dass ein Datum existiert
    end_date: task.start_date
      ? new Date(new Date(task.start_date).getTime() + task.estimated_hours * 60 * 60 * 1000)
      : new Date(new Date().getTime() + task.estimated_hours * 60 * 60 * 1000),
    type: 'task' as const,
  }));

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

