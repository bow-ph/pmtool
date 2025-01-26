import React, { useState } from 'react';
import { PdfAnalysisResponse } from '../../types/api';
import PDFUploader from './PDFUploader';
import AnalysisResults from './AnalysisResults';

interface PDFAnalysisContainerProps {
  projectId: number;
}

const PDFAnalysisContainer: React.FC<PDFAnalysisContainerProps> = ({ projectId }) => {
  const [analysisResult, setAnalysisResult] = useState<PdfAnalysisResponse | null>(null);

  const handleAnalysisComplete = (result: PdfAnalysisResponse) => {
    setAnalysisResult(result);
  };

  return (
    <div className={cn("space-y-6")}>
      <PDFUploader projectId={projectId} onAnalysisComplete={handleAnalysisComplete} />
      
      {analysisResult?.document_analysis && analysisResult?.confidence_analysis && (
        <AnalysisResults
          tasks={analysisResult.tasks}
          totalEstimatedHours={analysisResult.total_estimated_hours}
          riskFactors={analysisResult.risk_factors}
          documentAnalysis={analysisResult.document_analysis}
          confidenceAnalysis={analysisResult.confidence_analysis}
        />
      )}
    </div>
  );
};

export default PDFAnalysisContainer;
