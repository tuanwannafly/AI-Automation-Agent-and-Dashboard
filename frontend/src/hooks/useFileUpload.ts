'use client';

import { useState, useCallback } from 'react';
import { useFileUploadStore } from '@/store/fileUploadStore';
import api from '@/lib/api';
import { v4 as uuidv4 } from 'uuid';

interface UseFileUploadOptions {
  onProgress?: (fileId: string, progress: number) => void;
  onComplete?: (fileId: string) => void;
  onError?: (fileId: string, error: string) => void;
}

export function useFileUpload(options: UseFileUploadOptions = {}) {
  const { addFile, updateFile, setIsUploading } = useFileUploadStore();
  const [uploadingFileId, setUploadingFileId] = useState<string | null>(null);

  const upload = useCallback(async (file: File) => {
    const fileId = uuidv4();
    setUploadingFileId(fileId);

    addFile({
      id: fileId,
      filename: file.name,
      size: file.size,
      type: file.name.endsWith('.pdf') ? 'pdf' : 'docx',
      status: 'uploading',
      progress: 0,
      uploadedAt: Date.now()
    });

    setIsUploading(true);

    try {
      const result = await api.uploadFile(file, (progress) => {
        updateFile(fileId, { progress });
        options.onProgress?.(fileId, progress);
      });

      updateFile(fileId, {
        status: result.status,
        progress: 100
      });

      options.onComplete?.(result.id);
      return result;
    } catch (error: any) {
      const errorMessage = error.message || 'Upload failed';
      updateFile(fileId, {
        status: 'error',
        error: errorMessage
      });
      options.onError?.(fileId, errorMessage);
      throw error;
    } finally {
      setIsUploading(false);
      setUploadingFileId(null);
    }
  }, [addFile, updateFile, setIsUploading, options]);

  return {
    upload,
    isUploading: uploadingFileId !== null,
    uploadingFileId
  };
}