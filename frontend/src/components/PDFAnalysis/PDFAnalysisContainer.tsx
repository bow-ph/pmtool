import React, { useState } from 'react';
import { PdfAnalysisResponse } from '@/types/api';
import PDFUploader from './PDFUploader';
import AnalysisResults from './AnalysisResults';
import { cn } from '@/utils';
import ProactiveHintsPanel from '../ProactiveHints/ProactiveHintsPanel';

interface PDFAnalysisContainerProps {
  projectId: number;
}

const PDFAnalysisContainer: React.FC<PDFAnalysisContainerProps> = ({ projectId }) => {
  const [analysisResult, setAnalysisResult] = useState<PdfAnalysisResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

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
        onPdfUploaded={setPdfUrl}
      />

      {isUploading && (
        <div className="mt-4">
          <p className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 font-medium">
            PDF wird hochgeladen...
          </p>
          <div className="relative w-full h-4 mt-2 bg-gradient-to-r from-blue-400/20 via-purple-400/20 to-pink-400/20 rounded-full overflow-hidden">
            <div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${uploadProgress}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent animate-shimmer"></div>
            </div>
          </div>
          <p className="text-sm text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 font-medium mt-1">
            {uploadProgress}% hochgeladen
          </p>
        </div>
      )}

      {uploadError && (
        <p className="mt-4 text-red-500 text-sm">Fehler beim Upload: {uploadError}</p>
      )}

      {analysisResult && (
        <>
          {analysisResult.hints && analysisResult.hints.length > 0 && (
            <ProactiveHintsPanel
              data={analysisResult}
              projectId={projectId}
            />
          )}
          <AnalysisResults
            tasks={analysisResult.tasks}
            totalEstimatedHours={analysisResult.total_estimated_hours}
            riskFactors={analysisResult.risk_factors}
            documentAnalysis={analysisResult.document_analysis}
            confidenceAnalysis={{
              ...analysisResult.confidence_analysis,
              accuracy_factors: [
                { name: 'Document Clarity', value: analysisResult.confidence_analysis.accuracy_factors.document_clarity },
                { name: 'Technical Complexity', value: analysisResult.confidence_analysis.accuracy_factors.technical_complexity },
                { name: 'Dependency Risk', value: analysisResult.confidence_analysis.accuracy_factors.dependency_risk },
                { name: 'Client Input Risk', value: analysisResult.confidence_analysis.accuracy_factors.client_input_risk }
              ],
            }}
          />
          {pdfUrl && (
            <div className="mt-6 rounded-lg overflow-hidden transform transition-all duration-300 hover:scale-[1.01] hover:shadow-xl">
              <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 p-1">
                <div className="bg-white rounded-t-lg px-4 py-2 flex items-center justify-between">
                  <h3 className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 font-medium">
                    Hochgeladenes PDF
                  </h3>
                </div>
              </div>
              <iframe
                src={pdfUrl}
                className="w-full h-[600px] border-0"
                title="Uploaded PDF"
              />
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default PDFAnalysisContainer;
