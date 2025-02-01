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
      className={`p-8 border-2 border-dashed rounded-lg text-center cursor-pointer transition-all duration-300 transform hover:scale-[1.02] ${
        isDragActive 
          ? 'border-transparent bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 shadow-lg' 
          : 'border-gray-300 hover:border-transparent hover:bg-gradient-to-r hover:from-blue-400/20 hover:via-purple-400/20 hover:to-pink-400/20'
      }`}
    >
      <input {...getInputProps()} />
      {uploadMutation.status === 'pending' ? (
        <div className="flex flex-col items-center">
          <div className="relative w-16 h-16 mb-3">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-lg animate-pulse"></div>
            <div className="absolute inset-1 bg-white rounded-lg flex items-center justify-center">
              <svg className="w-8 h-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-bounce" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>
          <p className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 font-medium">
            PDF wird hochgeladen...
          </p>
        </div>
      ) : (
        <div>
          {isDragActive ? (
            <p className="text-white font-medium text-lg">PDF hier ablegen...</p>
          ) : (
            <div className="space-y-2">
              <p className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 font-medium text-lg">
                PDF hier ablegen oder klicken zum Hochladen
              </p>
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
