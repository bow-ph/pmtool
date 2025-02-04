import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Task } from '../types/api';
import TodoList from '../components/TodoList/TodoList';
import { apiClient } from '../api/client';
import { toast } from 'react-hot-toast';
import CalendarSubscription from '../components/Calendar/CalendarSubscription';

const Planning: React.FC = () => {
  const queryClient = useQueryClient();
  const { data: tasks = [] } = useQuery<Task[]>({
    queryKey: ['planning-tasks'],
    queryFn: async () => {
      const response = await apiClient.get('/tasks/planning');
      return response.data;
    }
  });

  const transferMutation = useMutation<void, Error, number[]>({
    mutationFn: async (taskIds) => {
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
            disabled={tasks.length === 0 || transferMutation.status === 'pending'}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>Send to Dashboard</span>
            <span>📤</span>
          </button>
        </div>

        <TodoList
          tasks={tasks}
          onStatusChange={async (taskId: number, status: 'pending' | 'in_progress' | 'completed') => {
            await apiClient.patch(`/tasks/${taskId}`, { status });
            queryClient.invalidateQueries({ queryKey: ['planning-tasks'] });
          }}
        />

        <CalendarSubscription
          userId={localStorage.getItem('userId') || ''}
          projectTitle="PM Tool"
        />
      </div>
    </div>
  );
};

export default Planning;
