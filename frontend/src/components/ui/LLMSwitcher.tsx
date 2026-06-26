'use client';

import { useSettingsStore } from '@/store/settingsStore';
import { useAgentStore } from '@/store/agentStore';
import { LLMProvider } from '@/types/agent';
import { ChevronDown, Check } from 'lucide-react';
import { useState } from 'react';

const PROVIDERS: { value: LLMProvider; label: string; description: string }[] = [
  { value: 'groq', label: 'Groq', description: 'Fast inference' },
  { value: 'openai', label: 'OpenAI', description: 'GPT models' },
  { value: 'gemini', label: 'Gemini', description: 'Google AI' }
];

export function LLMSwitcher() {
  const { defaultProvider, setDefaultProvider } = useSettingsStore();
  const { setProvider } = useAgentStore();
  const [isOpen, setIsOpen] = useState(false);

  const currentProvider = PROVIDERS.find(p => p.value === defaultProvider);

  const handleSelect = (provider: LLMProvider) => {
    setDefaultProvider(provider);
    setProvider(provider);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            defaultProvider === 'groq' ? 'bg-orange-500' :
            defaultProvider === 'openai' ? 'bg-green-500' : 'bg-blue-500'
          }`} />
          <span className="text-sm text-gray-300">{currentProvider?.label}</span>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="absolute right-0 top-full mt-1 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-50">
          {PROVIDERS.map((provider) => (
            <button
              key={provider.value}
              onClick={() => handleSelect(provider.value)}
              className="w-full px-4 py-3 text-left hover:bg-gray-700 first:rounded-t-lg last:rounded-b-lg transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    provider.value === 'groq' ? 'bg-orange-500' :
                    provider.value === 'openai' ? 'bg-green-500' : 'bg-blue-500'
                  }`} />
                  <span className="text-sm text-gray-300">{provider.label}</span>
                </div>
                {provider.value === defaultProvider && (
                  <Check className="w-4 h-4 text-green-400" />
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1 ml-4">{provider.description}</p>
            </button>
          ))}
        </div>
      )}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}