import React from 'react';
import { TodoItem, TodoFilter, TodoSyncStatus } from '../../types/todo';
import TodoListItem from './TodoListItem';
import TodoFilters from './TodoFilters';

interface TodoListProps {
  items: TodoItem[];
  filters: TodoFilter;
  syncStatus: TodoSyncStatus;
  onFilterChange: (filters: TodoFilter) => void;
  onItemUpdate: (itemId: number, updates: Partial<TodoItem>) => void;
}

const TodoList: React.FC<TodoListProps> = ({
  items,
  filters,
  syncStatus,
  onFilterChange,
  onItemUpdate,
}) => {
  // Sicherstellen, dass syncStatus existiert
  const isSyncStatusValid = syncStatus && typeof syncStatus.status === 'string';

  return (
    <div className="space-y-4">
      {/* Header mit Synchronisierungsstatus */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Aufgaben</h2>
        <div className="flex items-center space-x-2">
          {isSyncStatusValid && (
            <span
              aria-live="polite"
              className={`text-sm ${syncStatus.status === 'synced'
                  ? 'text-green-600'
                  : syncStatus.status === 'pending'
                    ? 'text-yellow-600'
                    : 'text-red-600'
                }`}
            >
              {syncStatus.status === 'synced'
                ? 'Synchronisiert'
                : syncStatus.status === 'pending'
                  ? 'Synchronisierung...'
                  : 'Synchronisierungsfehler'}
            </span>
          )}
          {syncStatus?.last_sync && (
            <span className="text-sm text-gray-500">
              Letzte Synchronisierung:{' '}
              {new Date(syncStatus.last_sync).toLocaleString()}
            </span>
          )}
        </div>
      </div>

      {/* Filter-Komponente */}
      {filters ? (
        <TodoFilters filters={filters} onChange={onFilterChange} />
      ) : (
        <p className="text-sm text-gray-500">
          Filterdaten nicht verfügbar.
        </p>
      )}

      {/* Aufgabenliste */}
      <div className="space-y-2">
        {items.length > 0 ? (
          <ul role="list" className="space-y-2">
            {items.map((item) => (
              <li key={item.id}>
                <TodoListItem
                  item={item}
                  onUpdate={(updates) => onItemUpdate(item.id, updates)}
                />
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-center text-gray-500 py-4">Keine Aufgaben gefunden</p>
        )}
      </div>
    </div>
  );
};

export default TodoList;
