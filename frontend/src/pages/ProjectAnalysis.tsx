import { useState } from 'react';
import PDFUploader from '../components/PDFAnalysis/PDFUploader';
import AnalysisResults from '../components/PDFAnalysis/AnalysisResults';
import ProactiveHintsPanel from '../components/ProactiveHints/ProactiveHintsPanel';
import { PdfAnalysisResponse, ProactiveHintsResponse } from '../types/api';
import { useQuery } from '@tanstack/react-query';
import { apiClient, endpoints } from '../api/client';

const ProjectAnalysis = () => {
  const [analysisResults, setAnalysisResults] = useState<PdfAnalysisResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
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
      return response.data;
    },
    enabled: !!projectId,
    onError: (error) => {
      console.error('Fehler beim Abrufen der proaktiven Hinweise:', error);
    },
  });

  // Handle successful analysis
  const handleAnalysisComplete = (results: PdfAnalysisResponse) => {
    console.log('Analyse abgeschlossen:', results); // Debugging
    setAnalysisResults(results);
    setUploadError(null); // Clear any previous upload errors
    setIsUploading(false); // Reset uploading state
  };

  // Handle upload error
  const handleUploadError = (error: string) => {
    console.error('Upload-Fehler:', error); // Log error
    setUploadError(error); // Set error state
    setIsUploading(false); // Reset uploading state
  };

  // Start uploading
  const handleUploadStart = () => {
    setIsUploading(true);
    setUploadError(null); // Clear previous errors before new upload
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">KI-Planung</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PDF Analyse */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">PDF Analyse</h2>

          <PDFUploader
            projectId={projectId}
            onAnalysisComplete={handleAnalysisComplete}
            onUploadStart={handleUploadStart}
            onError={handleUploadError}
          />

          {isUploading && (
            <p className="mt-4 text-blue-500 text-sm">PDF wird hochgeladen und analysiert...</p>
          )}

          {uploadError && (
            <p className="mt-4 text-red-500 text-sm">
              Fehler beim Upload: {uploadError}
            </p>
          )}

          {analysisResults && (
            <div className="mt-8">
              <AnalysisResults
                tasks={analysisResults.tasks.map((task) => ({
                  ...task,
                  title: task.description,
                }))}
                totalEstimatedHours={analysisResults.total_estimated_hours}
                riskFactors={analysisResults.risk_factors}
                documentAnalysis={analysisResults.document_analysis}
                confidenceAnalysis={analysisResults.confidence_analysis}
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
            proactiveHints && <ProactiveHintsPanel data={proactiveHints} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectAnalysis;