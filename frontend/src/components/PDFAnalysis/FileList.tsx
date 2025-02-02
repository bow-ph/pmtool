import React from 'react';
import { format } from 'date-fns';
import { FileIcon } from 'lucide-react';
import { UploadedPdfFile } from '../../types/api';

interface FileListProps {
  files: UploadedPdfFile[];
  onAnalyze: (file: UploadedPdfFile) => void;
  analyzingFile?: string;
}

export const FileList: React.FC<FileListProps> = ({ files, onAnalyze, analyzingFile }) => {
  return (
    <div className="mt-6 space-y-4">
      {files.map((file) => (
        <div
          key={file.file_url}
          className="flex items-center p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all"
        >
          <FileIcon className="h-6 w-6 text-blue-500 mr-3 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {file.filename}
            </p>
            <p className="text-sm text-gray-500">
              {format(new Date(file.upload_time), 'dd.MM.yyyy HH:mm')}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <a
              href={file.file_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-blue-600 hover:text-blue-500"
            >
              Öffnen
            </a>
            <button
              onClick={() => onAnalyze(file)}
              disabled={analyzingFile === file.stored_filename}
              className="px-3 py-1 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {analyzingFile === file.stored_filename ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analysiere...
                </span>
              ) : (
                'Planen'
              )}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
