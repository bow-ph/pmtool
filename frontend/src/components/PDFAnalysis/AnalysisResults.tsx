import React from 'react';
import { Task } from '../../types/api';

interface AnalysisResultsProps {
  tasks: Task[];
  totalEstimatedHours: number;
  riskFactors: string[];
  confidenceAnalysis?: {
    overall_confidence: number;
    rationale: string;
    improvement_suggestions: string[];
  };
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  tasks,
  totalEstimatedHours,
  riskFactors,
  confidenceAnalysis,
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
                  {task.confidence_rationale && (
                    <p className="text-sm text-gray-600 mt-2 italic">
                      {task.confidence_rationale}
                    </p>
                  )}
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

      {confidenceAnalysis && (
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-2">Konfidenzanalyse</h4>
          <div className="bg-white shadow rounded-lg p-4 border border-gray-200">
            <div className="flex items-center mb-2">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mr-2
                  ${
                    confidenceAnalysis.overall_confidence >= 0.8
                      ? 'bg-green-100 text-green-800'
                      : confidenceAnalysis.overall_confidence >= 0.6
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}
              >
                {Math.round(confidenceAnalysis.overall_confidence * 100)}% Gesamtkonfidenz
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-3">{confidenceAnalysis.rationale}</p>
            {confidenceAnalysis.improvement_suggestions.length > 0 && (
              <div>
                <h5 className="text-sm font-medium text-gray-900 mb-1">Verbesserungsvorschläge</h5>
                <ul className="list-disc list-inside space-y-1">
                  {confidenceAnalysis.improvement_suggestions.map((suggestion, index) => (
                    <li key={index} className="text-sm text-gray-600">
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
