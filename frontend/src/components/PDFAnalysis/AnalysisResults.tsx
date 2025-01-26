import React from 'react';
import { Task } from '../../types/api';
import { PdfAnalysisResponse } from '../../types/api';
import { cn } from '../../utils';

interface AnalysisResultsProps {
  tasks: Task[];
  totalEstimatedHours: number;
  riskFactors: string[];
  documentAnalysis?: PdfAnalysisResponse['document_analysis'];
  confidenceAnalysis?: PdfAnalysisResponse['confidence_analysis'];
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  tasks,
  totalEstimatedHours,
  riskFactors,
  documentAnalysis,
  confidenceAnalysis,
}) => {
  // Early return if required data is missing
  if (!tasks?.length || !documentAnalysis || !confidenceAnalysis) {
    return null;
  }

  // Ensure all required properties exist
  if (!documentAnalysis.clarity_score || !documentAnalysis.type || !confidenceAnalysis.overall_confidence) {
    return null;
  }

  return (
    <div className={cn("space-y-6")}>
      <div className={cn("bg-white shadow rounded-lg p-6")}>
        <h3 className={cn("text-lg font-medium text-gray-900 mb-4")}>Dokumentanalyse</h3>
        <div className={cn("grid grid-cols-2 gap-4 mb-4")}>
          <div>
            <p className={cn("text-sm font-medium text-gray-500")}>Dokumenttyp</p>
            <p className={cn("mt-1 text-sm text-gray-900 capitalize")}>{documentAnalysis?.type || 'Unbekannt'}</p>
          </div>
          <div>
            <p className={cn("text-sm font-medium text-gray-500")}>Kundentyp</p>
            <p className={cn("mt-1 text-sm text-gray-900 capitalize")}>{documentAnalysis?.client_type || 'Unbekannt'}</p>
          </div>
          <div>
            <p className={cn("text-sm font-medium text-gray-500")}>Komplexität</p>
            <p className={cn("mt-1 text-sm text-gray-900 capitalize")}>{documentAnalysis?.complexity_level || 'Mittel'}</p>
          </div>
          <div>
            <p className={cn("text-sm font-medium text-gray-500")}>Dokumentklarheit</p>
            <div className={cn("mt-1 flex items-center")}>
              <div className={cn("w-24 bg-gray-200 rounded-full h-2")}>
                <div
                  className={cn("h-2 rounded-full", {
                    'bg-green-500': documentAnalysis.clarity_score >= 0.8,
                    'bg-yellow-500': documentAnalysis.clarity_score >= 0.6 && documentAnalysis.clarity_score < 0.8,
                    'bg-red-500': documentAnalysis.clarity_score < 0.6
                  })}
                  style={{ width: `${Math.round(documentAnalysis.clarity_score * 100)}%` }}
                />
              </div>
              <span className={cn("ml-2 text-sm text-gray-600")}>
                {Math.round(documentAnalysis.clarity_score * 100)}%
              </span>
            </div>
          </div>
        </div>
        <p className={cn("text-sm text-gray-600")}>{documentAnalysis.context || 'Keine Kontextinformationen verfügbar'}</p>
      </div>

      <div className={cn("bg-white shadow rounded-lg p-6")}>
        <div className={cn("flex justify-between items-center mb-4")}>
          <h3 className={cn("text-lg font-medium text-gray-900")}>Analyseergebnisse</h3>
          <p className={cn("text-sm text-gray-500")}>
            Geschätzte Gesamtzeit: <span className={cn("font-medium")}>{totalEstimatedHours} Stunden</span>
          </p>
        </div>

        <div className={cn("grid grid-cols-2 gap-4 mb-6")}>
          <div>
            <p className={cn("text-sm font-medium text-gray-500")}>Gesamtvertrauen</p>
            <div className={cn("mt-1 flex items-center")}>
              <div className={cn("w-24 bg-gray-200 rounded-full h-2")}>
                <div
                  className={cn("h-2 rounded-full", {
                    'bg-green-500': confidenceAnalysis.overall_confidence >= 0.8,
                    'bg-yellow-500': confidenceAnalysis.overall_confidence >= 0.6 && confidenceAnalysis.overall_confidence < 0.8,
                    'bg-red-500': confidenceAnalysis.overall_confidence < 0.6
                  })}
                  style={{ width: `${Math.round(confidenceAnalysis.overall_confidence * 100)}%` }}
                />
              </div>
              <span className="ml-2 text-sm text-gray-600">
                {Math.round(confidenceAnalysis.overall_confidence * 100)}%
              </span>
            </div>
          </div>
          {Object.entries(confidenceAnalysis.accuracy_factors || {}).map(([key, value]) => (
            <div key={key}>
              <p className={cn("text-sm font-medium text-gray-500 capitalize")}>
                {key.replace(/_/g, ' ')}
              </p>
              <div className={cn("mt-1 flex items-center")}>
                <div className={cn("w-24 bg-gray-200 rounded-full h-2")}>
                  <div
                    className={cn("h-2 rounded-full", {
                      'bg-green-500': value >= 0.8,
                      'bg-yellow-500': value >= 0.6 && value < 0.8,
                      'bg-red-500': value < 0.6
                    })}
                    style={{ width: `${Math.round(value * 100)}%` }}
                  />
                </div>
                <span className={cn("ml-2 text-sm text-gray-600")}>
                  {Math.round(value * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className={cn("space-y-4")}>
          <h4 className={cn("text-md font-medium text-gray-900")}>Aufgaben</h4>
          {tasks.map((task, index) => (
            <div
              key={index}
              className={cn("bg-gray-50 rounded-lg p-4 border border-gray-200")}
            >
              <div className={cn("flex justify-between items-start")}>
                <div className={cn("flex-1")}>
                  <div className={cn("flex items-center")}>
                    <p className={cn("text-sm font-medium text-gray-900")}>
                      {task.description}
                    </p>
                    {task.requires_client_input && (
                      <span className={cn("ml-2 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full")}>
                        Kundeninput erforderlich
                      </span>
                    )}
                  </div>
                  <div className={cn("mt-2 grid grid-cols-2 gap-2")}>
                    <p className={cn("text-sm text-gray-500")}>
                      Geschätzte Zeit: {task.estimated_hours} Stunden
                    </p>
                    <p className={cn("text-sm text-gray-500")}>
                      Komplexität: <span className={cn("capitalize")}>{task.complexity || 'medium'}</span>
                    </p>
                  </div>
                  {task.technical_requirements && task.technical_requirements.length > 0 && (
                    <div className={cn("mt-2")}>
                      <p className={cn("text-sm text-gray-500")}>Technische Anforderungen:</p>
                      <ul className={cn("mt-1 list-disc list-inside text-sm text-gray-600")}>
                        {task.technical_requirements.map((req, i) => (
                          <li key={i}>{req}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {task.confidence_rationale && (
                    <p className={cn("text-sm text-gray-600 mt-2 italic")}>
                      {task.confidence_rationale}
                    </p>
                  )}
                </div>
                <div className={cn("ml-4")}>
                  <span
                    className={cn("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium", {
                      'bg-green-100 text-green-800': task.confidence_score >= 0.8,
                      'bg-yellow-100 text-yellow-800': task.confidence_score >= 0.6 && task.confidence_score < 0.8,
                      'bg-red-100 text-red-800': task.confidence_score < 0.6
                    })}
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
        <div className={cn("bg-white shadow rounded-lg p-6")}>
          <h4 className={cn("text-md font-medium text-gray-900 mb-4")}>Risikofaktoren</h4>
          <ul className={cn("space-y-2")}>
            {riskFactors.map((risk, index) => (
              <li key={index} className={cn("flex items-start")}>
                <span className={cn("flex-shrink-0 h-5 w-5 text-yellow-500")}>
                  ⚠️
                </span>
                <span className={cn("ml-2 text-sm text-gray-600")}>{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {confidenceAnalysis.improvement_suggestions?.length > 0 && (
        <div className={cn("bg-white shadow rounded-lg p-6")}>
          <h4 className={cn("text-md font-medium text-gray-900 mb-4")}>Verbesserungsvorschläge</h4>
          <div className={cn("space-y-3")}>
            {confidenceAnalysis.improvement_suggestions?.map((suggestion, index) => (
              <div key={index} className={cn("flex items-start")}>
                <span className={cn("flex-shrink-0 h-5 w-5 text-blue-500")}>
                  💡
                </span>
                <p className={cn("ml-2 text-sm text-gray-600")}>{suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
