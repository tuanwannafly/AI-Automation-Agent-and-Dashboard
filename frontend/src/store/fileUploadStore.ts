import { create } from 'zustand';
import { UploadedFile } from '@/types/file';

interface FileUploadStore {
  files: UploadedFile[];
  isUploading: boolean;
  
  addFile: (file: UploadedFile) => void;
  updateFile: (id: string, updates: Partial<UploadedFile>) => void;
  removeFile: (id: string) => void;
  setIsUploading: (isUploading: boolean) => void;
  clearFiles: () => void;
}

export const useFileUploadStore = create<FileUploadStore>((set) => ({
  files: [],
  isUploading: false,
  
  addFile: (file) => set((state) => ({
    files: [...state.files, file]
  })),
  
  updateFile: (id, updates) => set((state) => ({
    files: state.files.map((f) => 
      f.id === id ? { ...f, ...updates } : f
    )
  })),
  
  removeFile: (id) => set((state) => ({
    files: state.files.filter((f) => f.id !== id)
  })),
  
  setIsUploading: (isUploading) => set({ isUploading }),
  
  clearFiles: () => set({ files: [] })
}));