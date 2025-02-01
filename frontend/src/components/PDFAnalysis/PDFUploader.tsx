import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient, endpoints } from '../../api/client';
import { PdfAnalysisResponse, UploadedPdfFile } from '../../types/api';
import { FileList } from './FileList';

interface PDFUploaderProps {
  projectId: number;
  onAnalysisComplete: (result: PdfAnalysisResponse) => void;
}

const PDFUploader: React.FC<PDFUploaderProps> = ({ projectId, onAnalysisComplete }) => {
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
      return response.data;
    },
    onSuccess: (data) => {
      onAnalysisComplete(data);
      refetchFiles();
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
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
            <p className="text-gray-600">Analysiere PDF...</p>
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
