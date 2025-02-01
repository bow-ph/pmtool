import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation } from '@tanstack/react-query';
import { AxiosResponse } from 'axios';
import { apiClient, endpoints } from '../../api/client';
import { PdfAnalysisResponse } from '../../types/api';

interface UploadResponse {
  pdf_url: string;
}

interface PDFUploaderProps {
  projectId: number;
  onAnalysisComplete: (result: PdfAnalysisResponse) => void;
  onUploadProgress?: (progress: number) => void;
  onUploadStart?: () => void;
  onError?: (error: string) => void;
  onPdfUploaded?: (pdfUrl: string) => void;
}

const PDFUploader: React.FC<PDFUploaderProps> = ({ 
  projectId, 
  onAnalysisComplete, 
  onUploadProgress,
  onUploadStart,
  onError,
  onPdfUploaded
}) => {
  const uploadMutation = useMutation<PdfAnalysisResponse, Error, File>({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      // First upload the PDF
      const uploadResponse: AxiosResponse<UploadResponse> = await apiClient.post(
        '/api/v1/pdf/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (onUploadProgress && progressEvent.total) {
              const progress = (progressEvent.loaded / progressEvent.total) * 100;
              onUploadProgress(progress);
            }
          },
        }
      );

      // Then analyze it
      const analysisResponse: AxiosResponse<PdfAnalysisResponse> = await apiClient.post(
        endpoints.analyzePdf(projectId),
        { pdf_url: uploadResponse.data.pdf_url },
        { headers: { 'Content-Type': 'application/json' } }
      );

      onPdfUploaded?.(uploadResponse.data.pdf_url);
      return analysisResponse.data;
    },
    onSuccess: onAnalysisComplete,
    onError: (error) => onError?.(error.message)
  });

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        if (file.size > 10 * 1024 * 1024) {
          onError?.('Die Datei darf nicht größer als 10 MB sein.');
          return;
        }
        onUploadStart?.();
        uploadMutation.mutate(file);
      }
    },
    [uploadMutation, onUploadStart, onError]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
  });

  return (
    <div
      {...getRootProps()}
      className={`p-8 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
        isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <input {...getInputProps()} />
      {uploadMutation.status === 'pending' ? ( // Status "pending" verwenden
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
          <p className="text-gray-600">PDF wird hochgeladen...</p>
        </div>
      ) : (
        <div>
          {isDragActive ? (
            <p className="text-blue-500">PDF hier ablegen...</p>
          ) : (
            <div className="space-y-2">
              <p className="text-gray-600">PDF hier ablegen oder klicken zum Hochladen</p>
              <p className="text-sm text-gray-500">(Nur PDF-Dateien, max. 10 MB)</p>
            </div>
          )}
        </div>
      )}
      {uploadMutation.status === 'error' && (
        <p className="mt-2 text-red-500 text-sm">
          Fehler beim Upload: {(uploadMutation.error as Error)?.message || 'Unbekannter Fehler'}
        </p>
      )}
    </div>
  );
};

export default PDFUploader;
