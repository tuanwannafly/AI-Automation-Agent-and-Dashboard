export interface UploadedFile {
  id: string;
  filename: string;
  size: number;
  type: 'pdf' | 'docx';
  status: 'uploading' | 'uploaded' | 'indexed' | 'error';
  progress?: number;
  error?: string;
  uploadedAt: number;
}