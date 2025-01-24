import React, { useState } from 'react';
import { TodoFilter } from '../../types/todo';
import { useTodoList } from '../../hooks/useTodoList';
import TodoList from './TodoList';
import TodoFilters from './TodoFilters';

interface TodoContainerProps {
  projectId: number;
}

const TodoContainer: React.FC<TodoContainerProps> = ({ projectId }) => {
  const [filters, setFilters] = useState<TodoFilter>({});
  const {
    todoList,
    isLoading,
    error,
    updateTodo,
    syncStatus,
    syncTodos,
    isSyncing,
  } = useTodoList(projectId, filters);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-600">
        Fehler beim Laden der Aufgaben
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Aufgabenliste</h2>
        <button
          onClick={() => syncTodos()}
          disabled={isSyncing}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            isSyncing
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isSyncing ? 'Synchronisiere...' : 'Jetzt synchronisieren'}
        </button>
      </div>

      <TodoFilters filters={filters} onChange={setFilters} />

      {todoList && (
        <TodoList
          items={todoList.items}
          filters={filters}
          syncStatus={syncStatus}
          onFilterChange={setFilters}
          onItemUpdate={(itemId, updates) => updateTodo({ todoId: itemId, updates })}
        />
      )}

      <div className="text-sm text-gray-500">
        Gesamt: {todoList?.total_items || 0} |
        Ausstehend: {todoList?.pending_items || 0} |
        In Bearbeitung: {todoList?.in_progress_items || 0} |
        Abgeschlossen: {todoList?.completed_items || 0}
      </div>
    </div>
  );
};

export default TodoContainer;
