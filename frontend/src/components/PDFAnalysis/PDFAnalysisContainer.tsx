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

  const handleAnalysisComplete = (result: PdfAnalysisResponse) => {
    setAnalysisResult(result);
  };

  return (
    <div className={cn("space-y-6")}>
      <PDFUploader projectId={projectId} onAnalysisComplete={handleAnalysisComplete} />
      
      {analysisResult && (
        <AnalysisResults
          tasks={analysisResult.tasks ?? []}
          totalEstimatedHours={analysisResult.total_estimated_hours ?? 0}
          riskFactors={analysisResult.risk_factors ?? []}
          documentAnalysis={analysisResult.document_analysis ?? undefined}
          confidenceAnalysis={analysisResult.confidence_analysis ?? undefined}
        />
      )}
    </div>
  );
};

export default PDFAnalysisContainer;
