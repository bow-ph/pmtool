import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Task } from '../types/api';
import TodoList from '../components/TodoList/TodoList';
import { apiClient } from '../api/client';
import { toast } from 'react-hot-toast';

const Planning: React.FC = () => {
  const queryClient = useQueryClient();
  const { data: tasks = [] } = useQuery<Task[]>({
    queryKey: ['planning-tasks'],
    queryFn: async () => {
      const response = await apiClient.get('/tasks/planning');
      return response.data;
    }
  });

  const transferMutation = useMutation({
    mutationFn: async (taskIds: number[]) => {
      await apiClient.post('/tasks/transfer', { taskIds });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planning-tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-tasks'] });
      toast.success('Tasks transferred to dashboard');
    },
    onError: (error: Error) => {
      toast.error(`Failed to transfer tasks: ${error.message}`);
    }
  });

  const handleTransferTasks = () => {
    const taskIds = tasks.map(task => task.id!).filter(Boolean);
    if (taskIds.length === 0) {
      toast.error('No tasks to transfer');
      return;
    }
    transferMutation.mutate(taskIds);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Task Planning</h1>
          <button
            onClick={handleTransferTasks}
            disabled={tasks.length === 0 || transferMutation.isLoading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>Send to Dashboard</span>
            <span>📤</span>
          </button>
        </div>

        <TodoList
          tasks={tasks}
          onTaskUpdate={async (taskId, updates) => {
            await apiClient.patch(`/tasks/${taskId}`, updates);
            queryClient.invalidateQueries({ queryKey: ['planning-tasks'] });
          }}
        />

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Calendar Subscription</h2>
          <p className="text-sm text-gray-600 mb-4">
            Subscribe to your tasks in your preferred calendar application:
          </p>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              readOnly
              value={`${window.location.origin}/api/v1/calendar/${localStorage.getItem('userId')}.ics`}
              className="flex-1 p-2 border rounded-md bg-white"
            />
            <button
              onClick={() => {
                navigator.clipboard.writeText(`${window.location.origin}/api/v1/calendar/${localStorage.getItem('userId')}.ics`);
                toast.success('Calendar URL copied to clipboard');
              }}
              className="bg-gray-200 hover:bg-gray-300 p-2 rounded-md"
            >
              📋
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Planning;
