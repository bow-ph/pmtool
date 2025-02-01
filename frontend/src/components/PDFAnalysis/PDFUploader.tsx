import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient, endpoints } from '../../api/client';
import { PdfAnalysisResponse, UploadedPdfFile } from '../../types/api';
import { FileList } from './FileList';
import { CheckCircle2 } from 'lucide-react';

interface PDFUploaderProps {
  projectId: number;
  onAnalysisComplete: (result: PdfAnalysisResponse) => void;
}

const PDFUploader: React.FC<PDFUploaderProps> = ({ projectId, onAnalysisComplete }) => {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showSuccess, setShowSuccess] = useState(false);

  const { data: uploadedFiles, refetch: refetchFiles } = useQuery({
    queryKey: ['uploadedFiles', projectId],
    queryFn: async () => {
      const response = await apiClient.get(endpoints.getUploadedPdfs(projectId));
      return response.data as UploadedPdfFile[];
    },
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      
      // First upload the file
      await apiClient.post(
        endpoints.uploadPdf(projectId),
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const progress = (progressEvent.loaded / progressEvent.total) * 100;
              setUploadProgress(Math.round(progress));
            }
          },
        }
      );
      
      // Then analyze it
      const response = await apiClient.post(
        endpoints.analyzePdf(projectId),
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 2000);
      return response.data;
    },
    onSuccess: (data) => {
      onAnalysisComplete(data);
      refetchFiles();
      setUploadProgress(0);
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      uploadMutation.mutate(acceptedFiles[0]);
    }
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`p-8 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
      >
        <input {...getInputProps()} />
        {uploadMutation.isPending ? (
          <div className="flex flex-col items-center">
            {showSuccess ? (
              <div className="flex flex-col items-center animate-bounce">
                <CheckCircle2 className="h-8 w-8 text-green-500 mb-2" />
                <p className="text-gray-600">Upload erfolgreich!</p>
              </div>
            ) : (
              <>
                <div className="relative mb-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent"></div>
                  {uploadProgress > 0 && (
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-xs font-medium">
                      {uploadProgress}%
                    </div>
                  )}
                </div>
                <p className="text-gray-600">
                  {uploadProgress === 100 ? 'Analysiere PDF...' : 'Lade PDF hoch...'}
                </p>
              </>
            )}
          </div>
        ) : (
          <div>
            {isDragActive ? (
              <p className="text-blue-500">PDF hier ablegen...</p>
            ) : (
              <div className="space-y-2">
                <p className="text-gray-600">PDF hier ablegen oder klicken zum Auswählen</p>
                <p className="text-sm text-gray-500">(Nur PDF-Dateien)</p>
              </div>
            )}
          </div>
        )}
        {uploadMutation.isError && (
          <p className="mt-2 text-red-500 text-sm">
            Fehler beim Upload: {(uploadMutation.error as Error).message}
          </p>
        )}
      </div>
      {uploadedFiles && uploadedFiles.length > 0 && (
        <FileList files={uploadedFiles} />
      )}
    </div>
  );
};

export default PDFUploader;
