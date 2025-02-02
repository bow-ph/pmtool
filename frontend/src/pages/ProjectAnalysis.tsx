import { useState } from 'react';
import PDFUploader from '../components/PDFAnalysis/PDFUploader';
import AnalysisResults from '../components/PDFAnalysis/AnalysisResults';
import { FileList } from '../components/PDFAnalysis/FileList';
import { PdfAnalysisResponse, UploadedPdfFile } from '../types/api';
import { useQuery } from '@tanstack/react-query';
import { apiClient, endpoints } from '@/api/client';

const ProjectAnalysis: React.FC = () => {
  const [analysisResults, setAnalysisResults] = useState<PdfAnalysisResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isMovingTasks, setIsMovingTasks] = useState(false);
  const projectId = 1; // TODO: Get from route params


  const { data: uploadedFiles, refetch: refetchFiles } = useQuery<UploadedPdfFile[]>({
    queryKey: ['uploadedFiles', projectId],
    queryFn: async () => {
      const response = await apiClient.get(endpoints.getUploadedPdfs(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });



  // Handle successful analysis
  const handleAnalysisComplete = async (results: PdfAnalysisResponse) => {
    console.log('Analyse abgeschlossen:', results);
    if (results.tasks && results.tasks.length > 0) {
      setAnalysisResults(results);
      setUploadError(null);
      setIsUploading(false);
      setUploadProgress(0);
    } else {
      // If no tasks were generated, show error
      setUploadError('Keine Aufgaben konnten aus dem PDF extrahiert werden.');
      setIsUploading(false);
      setUploadProgress(0);
    }
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
                    const storedFilename = file.stored_filename || file.filename;
                    if (!storedFilename) {
                      handleUploadError('Dateiname nicht gefunden');
                      return;
                    }
                    setIsUploading(true);
                    setUploadError(null);
                    console.log('Starting analysis for:', storedFilename);
                    try {
                      const response = await apiClient.post(
                        endpoints.analyzePdf(projectId, storedFilename)
                      );
                      if (response.data && response.data.tasks && response.data.tasks.length > 0) {
                        handleAnalysisComplete(response.data);
                      } else {
                        handleUploadError('Keine Aufgaben konnten aus dem PDF extrahiert werden.');
                      }
                    } catch (error: unknown) {
                      console.error('Error analyzing PDF:', error);
                      if (error && typeof error === 'object' && 'response' in error && 
                          error.response && typeof error.response === 'object' && 
                          'status' in error.response && error.response.status === 404) {
                        handleUploadError('PDF-Datei nicht gefunden. Bitte laden Sie die Datei erneut hoch.');
                      } else {
                        handleUploadError('Fehler bei der PDF-Analyse. Bitte versuchen Sie es später erneut.');
                      }
                    } finally {
                      setIsUploading(false);
                    }
                  } catch (error) {
                    console.error('Analysis error:', error);
                    handleUploadError(
                      error instanceof Error && error.message ? 
                      error.message : 
                      'Analyse fehlgeschlagen. Bitte versuchen Sie es erneut.'
                    );
                  } finally {
                    setIsUploading(false);
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
                className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={async () => {
                  try {
                    setIsMovingTasks(true);
                    for (const task of analysisResults.tasks) {
                      await apiClient.post(
                        endpoints.createTask(),
                        {
                          title: task.description,
                          description: task.description,
                          duration_hours: task.duration_hours || task.estimated_hours,
                          hourly_rate: task.hourly_rate,
                          status: 'pending',
                          priority: 'medium',
                          project_id: projectId
                        }
                      );
                    }
                    setAnalysisResults(null);
                    setIsMovingTasks(false);
                    refetchFiles();  // Refresh the file list after tasks are created
                  } catch (error) {
                    console.error('Failed to create tasks:', error);
                    handleUploadError(error instanceof Error ? error.message : 'Failed to create tasks');
                    setIsMovingTasks(false);
                  }
                }}
                disabled={isMovingTasks}
              >
                {isMovingTasks ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Plane ein...
                  </span>
                ) : (
                  'Einplanen'
                )}
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
