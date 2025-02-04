import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../api/client';
import CalendarSubscription from '../components/Calendar/CalendarSubscription';

interface Task {
  id: number;
  title: string;
  description: string;
  duration_hours: number;
  priority: string;
}

export default function Planning() {
  const { projectId } = useParams();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTasks, setSelectedTasks] = useState<number[]>([]);
  const [isTransferring, setIsTransferring] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, [projectId]);

  const fetchTasks = async () => {
    try {
      const response = await apiClient.get(`/api/v1/todo?project_id=${projectId}`);
      setTasks(response.data.items || []);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  };

  const handleTaskSelect = (taskId: number) => {
    setSelectedTasks(prev => 
      prev.includes(taskId) 
        ? prev.filter(id => id !== taskId)
        : [...prev, taskId]
    );
  };

  const handleTransferTasks = async () => {
    if (!selectedTasks.length) return;
    
    setIsTransferring(true);
    try {
      await apiClient.post('/api/v1/todo/transfer', { task_ids: selectedTasks });
      setSelectedTasks([]);
      fetchTasks();
    } catch (error) {
      console.error('Failed to transfer tasks:', error);
    } finally {
      setIsTransferring(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Project Planning</h1>
      
      <CalendarSubscription projectId={projectId} />
      
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Tasks</h2>
        <div className="space-y-4">
          {tasks.map(task => (
            <div key={task.id} className="flex items-center p-4 bg-white rounded-lg shadow">
              <input
                type="checkbox"
                checked={selectedTasks.includes(task.id)}
                onChange={() => handleTaskSelect(task.id)}
                className="mr-4"
              />
              <div>
                <h3 className="font-medium">{task.title}</h3>
                <p className="text-gray-600">{task.description}</p>
                <div className="text-sm text-gray-500">
                  Duration: {task.duration_hours}h | Priority: {task.priority}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {selectedTasks.length > 0 && (
          <button
            onClick={handleTransferTasks}
            disabled={isTransferring}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isTransferring ? 'Transferring...' : `Transfer ${selectedTasks.length} Tasks to Dashboard`}
          </button>
        )}
      </div>
    </div>
  );
}
