'use client';

import { useFileUploadStore } from '@/store/fileUploadStore';
import { File, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { useState } from 'react';
import api from '@/lib/api';

export function UploadedFileList() {
  const { files, removeFile } = useFileUploadStore();
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (fileId: string) => {
    setDeletingId(fileId);
    try {
      await api.deleteFile(fileId);
    } catch (error) {
      console.error('Failed to delete file from server:', error);
    } finally {
      removeFile(fileId);
      setDeletingId(null);
    }
  };

  if (files.length === 0) return null;

  return (
    <div className="mt-4 space-y-2">
      <h3 className="text-sm font-semibold text-gray-400 mb-2">Uploaded Files</h3>
      {files.map((file) => (
        <div
          key={file.id}
          className="flex items-center justify-between bg-gray-800 rounded-lg p-3 border border-gray-700"
        >
          <div className="flex items-center gap-3">
            <File className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-300">{file.filename}</p>
              <p className="text-xs text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {file.status === 'uploading' && (
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                <span className="text-xs text-blue-400">{file.progress?.toFixed(0)}%</span>
              </div>
            )}
            {file.status === 'uploaded' && (
              <CheckCircle className="w-4 h-4 text-green-400" />
            )}
            {file.status === 'indexed' && (
              <span className="text-xs bg-green-900/50 text-green-400 px-2 py-1 rounded">
                Indexed
              </span>
            )}
            {file.status === 'error' && (
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-red-400" />
                <span className="text-xs text-red-400">{file.error}</span>
              </div>
            )}
            <button
              onClick={() => handleDelete(file.id)}
              disabled={deletingId === file.id}
              className="p-1 hover:bg-gray-700 rounded transition-colors disabled:opacity-50"
            >
              {deletingId === file.id ? (
                <Loader2 className="w-4 h-4 text-gray-500 animate-spin" />
              ) : (
                <XCircle className="w-4 h-4 text-gray-500 hover:text-gray-300" />
              )}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}