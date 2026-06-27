'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X } from 'lucide-react';
import { useFileUploadStore } from '@/store/fileUploadStore';
import api from '@/lib/api';
import { v4 as uuidv4 } from 'uuid';

interface FileUploadZoneProps {
  onFileUploaded?: (fileId: string) => void;
}

const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
};

const MAX_SIZE = 20 * 1024 * 1024; // 20MB

export function FileUploadZone({ onFileUploaded }: FileUploadZoneProps) {
  const { addFile, updateFile, setIsUploading } = useFileUploadStore();
  const [dragActive, setDragActive] = useState(false);

  const uploadFile = async (file: File) => {
    const fileId = uuidv4();
    
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
      });

      updateFile(fileId, {
        id: result.id,
        status: result.status,
        progress: 100
      });

      onFileUploaded?.(result.id);
    } catch (error) {
      console.error('Upload failed:', error);
      updateFile(fileId, {
        status: 'error',
        error: 'Upload failed'
      });
    } finally {
      setIsUploading(false);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    rejectedFiles.forEach((rejected) => {
      if (rejected.errors[0]?.code === 'file-too-large') {
        alert('File is too large. Max size is 20MB.');
      } else if (rejected.errors[0]?.code === 'file-invalid-type') {
        alert('Invalid file type. Only PDF and DOCX are accepted.');
      }
    });

    acceptedFiles.forEach((file) => {
      if (file.size > MAX_SIZE) {
        alert('File is too large. Max size is 20MB.');
        return;
      }
      uploadFile(file);
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
        ${isDragActive || dragActive 
          ? 'border-purple-500 bg-purple-900/20' 
          : 'border-gray-700 hover:border-gray-600 bg-gray-800'
        }`}
      onDragEnter={(e) => {
        e.preventDefault();
        setDragActive(true);
      }}
      onDragLeave={(e) => {
        e.preventDefault();
        setDragActive(false);
      }}
      onDragOver={(e) => e.preventDefault()}
    >
      <input {...getInputProps()} />
      <Upload className="w-12 h-12 mx-auto mb-4 text-gray-500" />
      <p className="text-gray-400 mb-2">
        {isDragActive ? 'Drop the file here...' : 'Drag & drop a PDF or DOCX file here'}
      </p>
      <p className="text-xs text-gray-500">or click to select (max 20MB)</p>
    </div>
  );
}