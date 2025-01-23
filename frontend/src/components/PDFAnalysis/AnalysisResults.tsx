import React from 'react';
import { Task } from '../../types/api';

interface AnalysisResultsProps {
  tasks: Task[];
  totalEstimatedHours: number;
  riskFactors: string[];
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  tasks,
  totalEstimatedHours,
  riskFactors,
}) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Analyseergebnisse</h3>
        <p className="text-sm text-gray-500">
          Geschätzte Gesamtzeit: {totalEstimatedHours} Stunden
        </p>
      </div>

      <div>
        <h4 className="text-md font-medium text-gray-900 mb-2">Aufgaben</h4>
        <div className="space-y-4">
          {tasks.map((task, index) => (
            <div
              key={index}
              className="bg-white shadow rounded-lg p-4 border border-gray-200"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {task.description}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Geschätzte Zeit: {task.estimated_hours} Stunden
                  </p>
                </div>
                <div className="ml-4">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                      ${
                        task.confidence_score >= 0.8
                          ? 'bg-green-100 text-green-800'
                          : task.confidence_score >= 0.6
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                  >
                    {Math.round(task.confidence_score * 100)}% Konfidenz
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {riskFactors.length > 0 && (
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-2">Risikofaktoren</h4>
          <ul className="list-disc list-inside space-y-1">
            {riskFactors.map((risk, index) => (
              <li key={index} className="text-sm text-gray-600">
                {risk}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
