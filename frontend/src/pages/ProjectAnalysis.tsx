import { useState } from 'react';

import PDFUploader from '../components/PDFAnalysis/PDFUploader';
import AnalysisResults from '../components/PDFAnalysis/AnalysisResults';

import { FileList } from '../components/PDFAnalysis/FileList';
import { PdfAnalysisResponse, UploadedPdfFile } from '../types/api';
import { useQuery } from '@tanstack/react-query';
import { apiClient, endpoints } from '@/api/client';

const ProjectAnalysis = () => {
  const [analysisResults, setAnalysisResults] = useState<PdfAnalysisResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const projectId = 1; // TODO: Get from route params


  const { data: uploadedFiles } = useQuery<UploadedPdfFile[]>({
    queryKey: ['uploadedFiles', projectId],
    queryFn: async () => {
      const response = await apiClient.get(endpoints.getUploadedPdfs(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });



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
          
          {uploadedFiles && uploadedFiles.length > 0 && (
            <div className="mt-6">
              <FileList 
                files={uploadedFiles}
                onAnalyze={async (file) => {
                  try {
                    const formData = new FormData();
                    formData.append('file', file.stored_filename);
                    const response = await apiClient.post(
                      endpoints.analyzePdf(projectId),
                      formData,
                      {
                        headers: {
                          'Content-Type': 'multipart/form-data',
                        }
                      }
                    );
                    handleAnalysisComplete(response.data);
                  } catch (error) {
                    handleUploadError(error instanceof Error ? error.message : 'Analysis failed');
                  }
                }}
              />
            </div>
          )}
          
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

        {/* Analysierte Aufgaben */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Analysierte Aufgaben</h2>
          {analysisResults?.tasks && analysisResults.tasks.length > 0 ? (
            <div className="space-y-4">
              <div className="divide-y divide-gray-200">
                {analysisResults.tasks.map((task, index) => (
                  <div key={index} className="py-4">
                    <h3 className="text-sm font-medium text-gray-900">{task.description}</h3>
                    <p className="mt-1 text-sm text-gray-600">{task.description}</p>
                    <div className="mt-2 flex items-center text-sm text-gray-500">
                      <span>Geschätzte Zeit: {task.estimated_hours} Stunden</span>
                      {task.duration_hours && (
                        <span className="ml-4">Dauer: {task.duration_hours} Stunden</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <button
                className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                onClick={async () => {
                  try {
                    await apiClient.post(
                      endpoints.createTasks(projectId),
                      {
                        tasks: analysisResults.tasks.map(task => ({
                          description: task.description,
                          estimated_hours: task.estimated_hours,
                          duration_hours: task.duration_hours,
                          status: 'pending',
                          priority: 'medium',
                          confidence_score: task.confidence_score,
                          confidence_rationale: task.confidence_rationale
                        }))
                      }
                    );
                    setAnalysisResults(null);
                  } catch (error) {
                    console.error('Failed to create tasks:', error);
                    handleUploadError(error instanceof Error ? error.message : 'Failed to create tasks');
                  }
                }}
              >
                Einplanen
              </button>
            </div>
          ) : (
            <p className="text-gray-500">Keine analysierten Aufgaben vorhanden</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectAnalysis;
