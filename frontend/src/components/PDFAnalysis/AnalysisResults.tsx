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
      {/* Dokumentanalyse */}
      <div className={cn('bg-white shadow rounded-lg p-6')}>
        <h3 className={cn('text-lg font-medium text-gray-900 mb-4')}>Dokumentanalyse</h3>
        <div className={cn('grid grid-cols-2 gap-4')}>
          <p>Dokumenttyp: {documentAnalysis.type || 'Unbekannt'}</p>
          <p>Kundentyp: {documentAnalysis.client_type || 'Unbekannt'}</p>
          <p>Komplexität: {documentAnalysis.complexity_level || 'Mittel'}</p>
          <p>Klarheit: {Math.round(documentAnalysis.clarity_score * 100)}%</p>
        </div>
        <p className={cn('mt-4 text-sm text-gray-600')}>
          Kontext: {documentAnalysis.context || 'Keine Kontextinformationen verfügbar.'}
        </p>
      </div>

      {/* Vertrauensanalyse */}
      <div className={cn('bg-white shadow rounded-lg p-6')}>
        <h3 className={cn('text-lg font-medium text-gray-900 mb-4')}>Vertrauensanalyse</h3>
        <p>Gesamtvertrauen: {Math.round(confidenceAnalysis.overall_confidence * 100)}%</p>
        <p className={cn('mt-2 text-sm text-gray-600')}>
          Begründung: {confidenceAnalysis.rationale || 'Keine Begründung verfügbar.'}
        </p>
        <div className={cn('mt-4')}>
          <h4 className={cn('text-md font-medium text-gray-900 mb-2')}>Genauigkeitsfaktoren:</h4>
          {confidenceAnalysis.accuracy_factors.map((factor, index) => (
            <p key={index} className={cn('text-sm text-gray-500')}>
              {factor.name}: {Math.round(factor.value * 100)}%
            </p>
          ))}
        </div>
        <div className={cn('mt-4')}>
          <h4 className={cn('text-md font-medium text-gray-900 mb-2')}>Verbesserungsvorschläge:</h4>
          {confidenceAnalysis.improvement_suggestions.length > 0 ? (
            confidenceAnalysis.improvement_suggestions.map((suggestion, index) => (
              <p key={index} className={cn('text-sm text-gray-600')}>
                - {suggestion}
              </p>
            ))
          ) : (
            <p className={cn('text-sm text-gray-500')}>Keine Vorschläge verfügbar.</p>
          )}
        </div>
      </div>

      {/* Aufgabenübersicht */}
      <div className={cn('bg-white shadow rounded-lg p-6')}>
        <h3 className={cn('text-lg font-medium text-gray-900 mb-4')}>Aufgabenübersicht</h3>
        <p className={cn('mb-4 text-sm text-gray-600')}>
          Geschätzte Gesamtzeit: {totalEstimatedHours} Stunden
        </p>
        {tasks.map((task, index) => (
          <div key={index} className={cn('bg-gray-50 rounded-lg p-4 mb-2')}>
            <p className={cn('font-medium text-gray-900')}>{task.title}</p>
            <p className={cn('text-sm text-gray-600')}>Beschreibung: {task.description}</p>
            <p className={cn('text-sm text-gray-600')}>
              Geschätzte Zeit: {task.estimated_hours} Stunden
            </p>
          </div>
        ))}
      </div>

      {/* Risikofaktoren */}
      {riskFactors.length > 0 && (
        <div className={cn('bg-white shadow rounded-lg p-6')}>
          <h3 className={cn('text-lg font-medium text-gray-900 mb-4')}>Risikofaktoren</h3>
          <ul className={cn('list-disc list-inside space-y-2')}>
            {riskFactors.map((factor, index) => (
              <li key={index} className={cn('text-sm text-gray-600')}>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
