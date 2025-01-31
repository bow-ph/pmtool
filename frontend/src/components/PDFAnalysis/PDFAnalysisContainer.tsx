import React, { useState } from 'react';
import { PdfAnalysisResponse } from '@/types/api';
import PDFUploader from './PDFUploader';
import AnalysisResults from './AnalysisResults';
import { cn } from '@/utils'; // Absoluter Import

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
