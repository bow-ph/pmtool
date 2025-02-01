import React from 'react';
import { format } from 'date-fns';
import { FileIcon } from 'lucide-react';
import { UploadedPdfFile } from '../../types/api';

interface FileListProps {
  files: UploadedPdfFile[];
}

export const FileList: React.FC<FileListProps> = ({ files }) => {
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
          <a
            href={file.file_url}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-4 text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Öffnen
          </a>
        </div>
      ))}
    </div>
  );
};
