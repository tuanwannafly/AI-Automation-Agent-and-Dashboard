export interface Settings {
  apiKeys: {
    groq?: string;
    openai?: string;
    gemini?: string;
  };
  preferences: {
    defaultProvider: LLMProvider;
    maxIterations: number;
    timeout: number;
    theme: 'dark' | 'light';
  };
}

export type LLMProvider = 'groq' | 'openai' | 'gemini';