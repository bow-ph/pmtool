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

// Corrected PDFAnalysisContainer.tsx
import React, { useState } from 'react';
import { PdfAnalysisResponse } from '../../types/api';
import PDFUploader from './PDFUploader';
import AnalysisResults from './AnalysisResults';
import { cn } from '../../utils';

interface PDFAnalysisContainerProps {
  projectId: number;
}

const PDFAnalysisContainer: React.FC<PDFAnalysisContainerProps> = ({ projectId }) => {
  const [analysisResult, setAnalysisResult] = useState<PdfAnalysisResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);

  const handleAnalysisComplete = (result: PdfAnalysisResponse) => {
    setAnalysisResult(result);
    setUploadError(null);
    setIsUploading(false);
    setUploadProgress(0);
  };

  const handleUploadStart = () => {
    setIsUploading(true);
    setUploadError(null);
    setUploadProgress(0);
  };

  const handleUploadProgress = (progress: number) => {
    setUploadProgress(progress);
  };

  const handleUploadError = (error: string) => {
    setUploadError(error);
    setIsUploading(false);
    setUploadProgress(0);
  };

  return (
    <div className={cn('space-y-6')}>
      <PDFUploader
        projectId={projectId}
        onAnalysisComplete={handleAnalysisComplete}
        onUploadStart={handleUploadStart}
        onUploadProgress={handleUploadProgress}
        onError={handleUploadError}
      />

      {isUploading && (
        <div className="mt-4">
          <p className="text-blue-500 text-sm">PDF wird hochgeladen...</p>
          <div className="relative w-full bg-gray-200 rounded h-4 mt-2">
            <div
              className="absolute top-0 left-0 h-4 bg-blue-500 rounded"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 mt-1">{uploadProgress}% hochgeladen</p>
        </div>
      )}

      {uploadError && (
        <p className="mt-4 text-red-500 text-sm">Fehler beim Upload: {uploadError}</p>
      )}

      {analysisResult && (
        <AnalysisResults
          tasks={analysisResult.tasks.map((task) => ({
            title: task.description,
            description: task.description,
            estimated_hours: task.estimated_hours,
          }))}
          totalEstimatedHours={analysisResult.total_estimated_hours}
          riskFactors={analysisResult.risk_factors}
          documentAnalysis={analysisResult.document_analysis}
          confidenceAnalysis={{
            ...analysisResult.confidence_analysis,
            accuracy_factors: Object.entries(
              analysisResult.confidence_analysis.accuracy_factors
            ).map(([key, value]) => ({ name: key.replace(/_/g, ' '), value })),
          }}
        />
      )}
    </div>
  );
};

export default PDFAnalysisContainer;
