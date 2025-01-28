import React, { useState } from 'react';
import { TodoItem } from '../../types/todo';

interface TodoListItemProps {
  item: TodoItem;
  onUpdate: (updates: Partial<TodoItem>) => void;
}

const TodoListItem: React.FC<TodoListItemProps> = ({ item, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [actualHours, setActualHours] = useState(item.actual_hours?.toString() || '');

  const handleStatusChange = (status: TodoItem['status']) => {
    if (status) {
      onUpdate({ status });
    }
  };

  const handleActualHoursSubmit = () => {
    const hours = parseFloat(actualHours);
    if (!isNaN(hours) && hours >= 0) {
      onUpdate({ actual_hours: hours });
      setIsEditing(false);
    } else {
      alert('Bitte geben Sie eine gültige Anzahl von Stunden ein.');
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-4 border border-gray-200">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          {/* Status und Priorität */}
          <div className="flex items-center space-x-2">
            <label htmlFor={`status-${item.id}`} className="sr-only">
              Status ändern
            </label>
            <select
              id={`status-${item.id}`}
              value={item.status}
              onChange={(e) => handleStatusChange(e.target.value as TodoItem['status'])}
              className="text-sm border-gray-300 rounded-md"
              aria-label="Status ändern"
            >
              <option value="pending">Ausstehend</option>
              <option value="in_progress">In Bearbeitung</option>
              <option value="completed">Abgeschlossen</option>
            </select>
            <span
              className={`px-2 py-1 text-xs rounded-full ${item.priority === 'high'
                  ? 'bg-red-100 text-red-800'
                  : item.priority === 'medium'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-green-100 text-green-800'
                }`}
              aria-label={`Priorität: ${item.priority}`}
            >
              {item.priority === 'high'
                ? 'Hoch'
                : item.priority === 'medium'
                  ? 'Mittel'
                  : 'Niedrig'}
            </span>
          </div>

          {/* Beschreibung und Stundenanzeige */}
          <p className="mt-2 text-sm text-gray-900">{item.description || 'Keine Beschreibung verfügbar'}</p>
          <div className="mt-1 text-sm text-gray-500">
            <span>Geschätzt: {item.estimated_hours ?? 'N/A'}h</span>
            {item.actual_hours !== undefined && (
              <span className="ml-2">Tatsächlich: {item.actual_hours}h</span>
            )}
          </div>
        </div>

        {/* Stundenbearbeitung */}
        <div className="ml-4 flex items-center space-x-2">
          {isEditing ? (
            <div className="flex items-center space-x-2">
              <label htmlFor={`actual-hours-${item.id}`} className="sr-only">
                Tatsächliche Stunden eingeben
              </label>
              <input
                id={`actual-hours-${item.id}`}
                type="number"
                value={actualHours}
                onChange={(e) => setActualHours(e.target.value)}
                className="w-20 text-sm border-gray-300 rounded-md"
                min="0"
                step="0.5"
                aria-label="Tatsächliche Stunden"
              />
              <button
                onClick={handleActualHoursSubmit}
                className="text-sm text-blue-600 hover:text-blue-800"
                aria-label="Speichern der tatsächlichen Stunden"
              >
                Speichern
              </button>
            </div>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="text-sm text-gray-600 hover:text-gray-800"
              aria-label="Zeit erfassen"
            >
              Zeit erfassen
            </button>
          )}
        </div>
      </div>

      {/* Konfidenz-Anzeige */}
      {item.confidence_rationale && (
        <div className="mt-2 text-sm text-gray-500">
          <span className="font-medium">Konfidenz: </span>
          {item.confidence_rationale}
        </div>
      )}
    </div>
  );
};

export default TodoListItem;
