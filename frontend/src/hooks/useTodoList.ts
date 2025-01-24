import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, endpoints } from '../api/client';
import { TodoItem, TodoFilter, TodoUpdateRequest, TodoList, TodoSyncStatus } from '../types/todo';

export const useTodoList = (projectId: number, filters: TodoFilter) => {
  const queryClient = useQueryClient();

  // Fetch todos
  const { data: todoList, isLoading, error } = useQuery<TodoList>({
    queryKey: ['todos', projectId, filters],
    queryFn: async () => {
      const response = await apiClient.get(endpoints.getTodos(projectId), {
        params: filters,
      });
      return response.data;
    },
  });

  // Update todo
  const updateTodo = useMutation({
    mutationFn: async ({ todoId, updates }: { todoId: number; updates: TodoUpdateRequest }) => {
      const response = await apiClient.put(endpoints.updateTodo(todoId), updates);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos', projectId] });
    },
  });

  // Sync status
  const { data: syncStatus } = useQuery<TodoSyncStatus>({
    queryKey: ['todoSync', projectId],
    queryFn: async () => {
      const response = await apiClient.get(endpoints.getSyncStatus(projectId));
      return response.data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Manual sync trigger
  const syncTodos = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(endpoints.syncTodos(projectId));
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos', projectId] });
      queryClient.invalidateQueries({ queryKey: ['todoSync', projectId] });
    },
  });

  return {
    todoList,
    isLoading,
    error,
    updateTodo: updateTodo.mutate,
    syncStatus: syncStatus || { status: 'pending' },
    syncTodos: syncTodos.mutate,
    isSyncing: syncTodos.isPending,
  };
};
