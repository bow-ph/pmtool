import { useState } from 'react';
import PDFUploader from '@/components/PDFAnalysis/PDFUploader';
import AnalysisResults from '@/components/PDFAnalysis/AnalysisResults';
import ProactiveHintsPanel from '@/components/ProactiveHints/ProactiveHintsPanel';
import { PdfAnalysisResponse, ProactiveHintsResponse } from '@/types/api';
import { useQuery } from '@tanstack/react-query';
import { apiClient, endpoints } from '@/api/client';

const ProjectAnalysis = () => {
  const [analysisResults, setAnalysisResults] = useState<PdfAnalysisResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const projectId = 1; // TODO: Get from route params

  // Fetch proactive hints for the project
  const {
    data: proactiveHints,
    isLoading: isLoadingHints,
    isError: isHintsError,
    error: hintsError,
  } = useQuery<ProactiveHintsResponse>({
    queryKey: ['proactiveHints', projectId],
    queryFn: async () => {
      const response = await apiClient.get(endpoints.getProactiveHints(projectId));
      const data = response.data as ProactiveHintsResponse;
      
      // Ensure all required properties are present with proper types
      if (!data.status || !data.financial_impact || !data.time_impact || !data.recommendations) {
        throw new Error('Unvollständige Daten von der API erhalten');
      }
      
      return data;
    },
    enabled: !!projectId,
  });

  if (isHintsError && hintsError) {
    console.error('Fehler beim Abrufen der proaktiven Hinweise:', hintsError);
  }

  // Handle successful analysis
  const handleAnalysisComplete = (results: PdfAnalysisResponse) => {
    console.log('Analyse abgeschlossen:', results);
    setAnalysisResults(results);
    setUploadError(null);
    setIsUploading(false);
    setUploadProgress(0);
  };

  // Handle upload error
  const handleUploadError = (error: string) => {
    console.error('Upload-Fehler:', error);
    setUploadError(error);
    setIsUploading(false);
    setUploadProgress(0);
  };

  // Start uploading
  const handleUploadStart = () => {
    setIsUploading(true);
    setUploadError(null);
    setUploadProgress(0);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">KI-Planung</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PDF Analyse */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">PDF Analyse</h2>
          <div className="space-y-4">
            <PDFUploader 
              projectId={projectId} 
              onAnalysisComplete={handleAnalysisComplete}
              onUploadProgress={(progress) => {
                setIsUploading(true);
                setUploadProgress(progress);
              }}
              onUploadStart={handleUploadStart}
              onError={handleUploadError}
            />
            {isUploading && (
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                  <span>Upload läuft... {uploadProgress.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 rounded-full h-2 transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            )}
            {uploadError && (
              <div className="text-sm text-red-500">
                {uploadError}
              </div>
            )}
          </div>
          
          {analysisResults && (
            <div className="mt-8">
              <AnalysisResults
                tasks={analysisResults.tasks.map((task) => ({
                  title: task.description, // Sicherstellen, dass 'title' vorhanden ist
                  description: task.description,
                  estimated_hours: task.estimated_hours,
                }))}
                totalEstimatedHours={analysisResults.total_estimated_hours}
                riskFactors={analysisResults.risk_factors}
                documentAnalysis={analysisResults.document_analysis}
                confidenceAnalysis={{
                  ...analysisResults.confidence_analysis,
                  accuracy_factors: Object.entries(
                    analysisResults.confidence_analysis.accuracy_factors
                  ).map(([key, value]) => ({
                    name: key.replace(/_/g, ' '),
                    value,
                  })),
                }}
              />
            </div>
          )}
        </div>

        {/* Proaktive Hinweise */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Proaktive Hinweise</h2>
          {isLoadingHints ? (
            <p className="text-gray-500">Lade proaktive Hinweise...</p>
          ) : isHintsError ? (
            <p className="text-red-500 text-sm">
              Fehler beim Abrufen der Hinweise: {(hintsError as Error)?.message || 'Unbekannter Fehler'}
            </p>
          ) : (
            proactiveHints && <ProactiveHintsPanel data={{ hints: analysisResults?.hints || [] }} projectId={projectId} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectAnalysis;
