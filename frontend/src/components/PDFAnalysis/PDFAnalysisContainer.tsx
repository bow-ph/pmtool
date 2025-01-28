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

  // Handle successful analysis completion
  const handleAnalysisComplete = (result: PdfAnalysisResponse) => {
    setAnalysisResult(result); // Save analysis result
    setUploadError(null); // Clear previous errors
    setIsUploading(false); // Reset uploading state
    setUploadProgress(0); // Reset progress
  };

  // Handle upload start
  const handleUploadStart = () => {
    setIsUploading(true);
    setUploadError(null); // Clear any previous error
    setUploadProgress(0); // Reset progress
  };

  // Handle upload progress
  const handleUploadProgress = (progress: number) => {
    setUploadProgress(progress);
  };

  // Handle upload error
  const handleUploadError = (error: string) => {
    setUploadError(error); // Save error message
    setIsUploading(false); // Reset uploading state
    setUploadProgress(0); // Reset progress
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

      {/* Upload progress */}
      {isUploading && (
        <div className="mt-4">
          <p className="text-blue-500 text-sm">PDF wird hochgeladen und analysiert...</p>
          <div className="relative w-full bg-gray-200 rounded h-4 mt-2">
            <div
              className="absolute top-0 left-0 h-4 bg-blue-500 rounded"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 mt-1">{uploadProgress}% hochgeladen</p>
        </div>
      )}

      {/* Upload error */}
      {uploadError && (
        <p className="text-red-500 text-sm mt-4">Fehler beim Upload: {uploadError}</p>
      )}

      {/* Analysis results */}
      {analysisResult && (
        <AnalysisResults
          tasks={analysisResult?.tasks.map((task) => ({
            ...task,
            title: task.description,
          })) ?? []}
          totalEstimatedHours={analysisResult?.total_estimated_hours ?? 0}
          riskFactors={analysisResult?.risk_factors ?? []}
          documentAnalysis={analysisResult?.document_analysis}
          confidenceAnalysis={analysisResult?.confidence_analysis}
        />
      )}
    </div>
  );
};

export default PDFAnalysisContainer;
