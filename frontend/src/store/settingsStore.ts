import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { LLMProvider } from '@/types/agent';

interface SettingsStore {
  apiKeys: {
    groq: string;
    openai: string;
    gemini: string;
  };
  defaultProvider: LLMProvider;
  maxIterations: number;
  timeout: number;
  theme: 'dark' | 'light';
  
  setApiKey: (provider: LLMProvider, key: string) => void;
  setDefaultProvider: (provider: LLMProvider) => void;
  setMaxIterations: (maxIterations: number) => void;
  setTimeout: (timeout: number) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  clearAll: () => void;
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      apiKeys: {
        groq: '',
        openai: '',
        gemini: ''
      },
      defaultProvider: 'groq',
      maxIterations: 10,
      timeout: 60000,
      theme: 'dark',
      
      setApiKey: (provider, key) => set((state) => ({
        apiKeys: { ...state.apiKeys, [provider]: key }
      })),
      
      setDefaultProvider: (provider) => set({ defaultProvider: provider }),
      setMaxIterations: (maxIterations) => set({ maxIterations }),
      setTimeout: (timeout) => set({ timeout }),
      setTheme: (theme) => set({ theme }),
      
      clearAll: () => set({
        apiKeys: { groq: '', openai: '', gemini: '' },
        defaultProvider: 'groq',
        maxIterations: 10,
        timeout: 60000,
        theme: 'dark'
      })
    }),
    {
      name: 'agent-settings'
    }
  )
);