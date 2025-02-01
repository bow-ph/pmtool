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
      <div className={cn('bg-white shadow-lg rounded-lg p-6 transform transition-all duration-300 hover:scale-[1.01] hover:shadow-xl')}>
        <h3 className={cn('text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-lg font-medium mb-4')}>
          Dokumentanalyse
        </h3>
        <div className={cn('grid grid-cols-2 gap-4')}>
          <div className="p-3 rounded-lg bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10">
            <p className="font-medium">Dokumenttyp: <span className="text-gray-700">{documentAnalysis.type || 'Unbekannt'}</span></p>
          </div>
          <div className="p-3 rounded-lg bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10">
            <p className="font-medium">Kundentyp: <span className="text-gray-700">{documentAnalysis.client_type || 'Unbekannt'}</span></p>
          </div>
          <div className="p-3 rounded-lg bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10">
            <p className="font-medium">Komplexität: <span className="text-gray-700">{documentAnalysis.complexity_level || 'Mittel'}</span></p>
          </div>
          <div className="p-3 rounded-lg bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10">
            <p className="font-medium">Klarheit: <span className="text-gray-700">{Math.round(documentAnalysis.clarity_score * 100)}%</span></p>
          </div>
        </div>
        <p className={cn('mt-4 text-sm text-gray-600 p-3 rounded-lg bg-gradient-to-r from-blue-400/5 via-purple-400/5 to-pink-400/5')}>
          Kontext: {documentAnalysis.context || 'Keine Kontextinformationen verfügbar.'}
        </p>
      </div>

      {/* Vertrauensanalyse */}
      <div className={cn('bg-white shadow-lg rounded-lg p-6 transform transition-all duration-300 hover:scale-[1.01] hover:shadow-xl')}>
        <h3 className={cn('text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-lg font-medium mb-4')}>
          Vertrauensanalyse
        </h3>
        <div className="p-4 rounded-lg bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10">
          <p className="font-medium">Gesamtvertrauen: <span className="text-gray-700">{Math.round(confidenceAnalysis.overall_confidence * 100)}%</span></p>
          <p className={cn('mt-2 text-sm text-gray-600')}>
            Begründung: {confidenceAnalysis.rationale || 'Keine Begründung verfügbar.'}
          </p>
        </div>
        <div className={cn('mt-4')}>
          <h4 className={cn('text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-md font-medium mb-2')}>
            Genauigkeitsfaktoren:
          </h4>
          <div className="space-y-2">
            {confidenceAnalysis.accuracy_factors.map((factor, index) => (
              <div key={index} className="p-3 rounded-lg bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10">
                <p className="text-sm">
                  <span className="font-medium">{factor.name}:</span>{' '}
                  <span className="text-gray-700">{Math.round(factor.value * 100)}%</span>
                </p>
              </div>
            ))}
          </div>
        </div>
        <div className={cn('mt-4')}>
          <h4 className={cn('text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-md font-medium mb-2')}>
            Verbesserungsvorschläge:
          </h4>
          <div className="p-3 rounded-lg bg-gradient-to-r from-blue-400/5 via-purple-400/5 to-pink-400/5">
            {confidenceAnalysis.improvement_suggestions.length > 0 ? (
              <div className="space-y-2">
                {confidenceAnalysis.improvement_suggestions.map((suggestion, index) => (
                  <p key={index} className="text-sm text-gray-600">
                    - {suggestion}
                  </p>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">Keine Vorschläge verfügbar.</p>
            )}
          </div>
        </div>
      </div>

      {/* Aufgabenübersicht */}
      <div className={cn('bg-white shadow-lg rounded-lg p-6 transform transition-all duration-300 hover:scale-[1.01] hover:shadow-xl')}>
        <h3 className={cn('text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-lg font-medium mb-4')}>
          Aufgabenübersicht
        </h3>
        <div className="p-4 rounded-lg bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10 mb-4">
          <p className="font-medium">
            Geschätzte Gesamtzeit: <span className="text-gray-700">{totalEstimatedHours} Stunden</span>
          </p>
        </div>
        <div className="space-y-3">
          {tasks.map((task, index) => (
            <div
              key={index}
              className="p-4 rounded-lg bg-gradient-to-r from-blue-400/5 via-purple-400/5 to-pink-400/5 transform transition-all duration-300 hover:from-blue-400/10 hover:via-purple-400/10 hover:to-pink-400/10"
            >
              <p className="font-medium text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500">
                {task.title}
              </p>
              <p className="text-sm text-gray-600 mt-2">Beschreibung: {task.description}</p>
              <p className="text-sm font-medium mt-2">
                Geschätzte Zeit: <span className="text-gray-700">{task.estimated_hours} Stunden</span>
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Risikofaktoren */}
      {riskFactors.length > 0 && (
        <div className={cn('bg-white shadow-lg rounded-lg p-6 transform transition-all duration-300 hover:scale-[1.01] hover:shadow-xl')}>
          <h3 className={cn('text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-lg font-medium mb-4')}>
            Risikofaktoren
          </h3>
          <div className="p-4 rounded-lg bg-gradient-to-r from-blue-400/5 via-purple-400/5 to-pink-400/5">
            <ul className="space-y-2">
              {riskFactors.map((factor, index) => (
                <li key={index} className="text-sm text-gray-600 flex items-start">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 mr-2">•</span>
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
