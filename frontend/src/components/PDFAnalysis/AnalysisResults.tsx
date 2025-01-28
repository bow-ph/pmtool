import React from 'react';
import { cn } from '@/utils';

interface AnalysisResultsProps {
  tasks: Array<{
    title: string;
    description: string;
    estimated_hours: number;
  }>;
  totalEstimatedHours: number;
  riskFactors: string[];
  documentAnalysis?: {
    type: string;
    client_type: string;
    complexity_level: string;
    clarity_score: number;
    context: string;
  };
  confidenceAnalysis?: {
    overall_confidence: number;
    rationale: string;
    improvement_suggestions: string[];
    accuracy_factors: Array<{ name: string; value: number }>;
  };
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  tasks,
  totalEstimatedHours,
  riskFactors,
  documentAnalysis,
  confidenceAnalysis,
}) => {
  if (!documentAnalysis || !confidenceAnalysis) {
    return (
      <p className={cn('text-sm text-gray-500 italic')}>
        Analyseergebnisse unvollständig. Bitte laden Sie das PDF erneut hoch.
      </p>
    );
  }

  return (
    <div className={cn('space-y-6')}>
      <div className={cn('bg-white shadow rounded-lg p-6')}>
        <h3 className={cn('text-lg font-medium text-gray-900 mb-4')}>Dokumentanalyse</h3>
        <div className={cn('grid grid-cols-2 gap-4')}>
          <p>Dokumenttyp: {documentAnalysis.type || 'Unbekannt'}</p>
          <p>Kundentyp: {documentAnalysis.client_type || 'Unbekannt'}</p>
        </div>
      </div>

      <div className={cn('bg-white shadow rounded-lg p-6')}>
        <h3 className={cn('text-lg font-medium text-gray-900 mb-4')}>Vertrauensfaktoren</h3>
        {confidenceAnalysis.accuracy_factors.map((factor, index) => (
          <p key={index} className={cn('text-sm text-gray-500')}>
            {factor.name}: {Math.round(factor.value * 100)}%
          </p>
        ))}
      </div>

      <div className={cn('space-y-4')}>
        <h4 className={cn('text-md font-medium text-gray-900')}>Aufgaben</h4>
        {tasks.map((task, index) => (
          <div key={index} className={cn('bg-gray-50 rounded-lg p-4')}>
            <p>{task.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnalysisResults;
