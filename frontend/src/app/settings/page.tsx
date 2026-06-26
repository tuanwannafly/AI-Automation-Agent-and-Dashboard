'use client';

import { useState } from 'react';
import { useSettingsStore } from '@/store/settingsStore';
import { Eye, EyeOff } from 'lucide-react';
import { LLMProvider } from '@/types/agent';

export default function SettingsPage() {
  const { apiKeys, defaultProvider, setApiKey, setDefaultProvider, clearAll } = useSettingsStore();
  const [visibleKeys, setVisibleKeys] = useState<Record<LLMProvider, boolean>>({
    groq: false,
    openai: false,
    gemini: false
  });

  const handleSaveKey = (provider: LLMProvider, key: string) => {
    setApiKey(provider, key);
  };

  const toggleVisibility = (provider: LLMProvider) => {
    setVisibleKeys(prev => ({ ...prev, [provider]: !prev[provider] }));
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <header className="border-b border-gray-700 bg-gray-800">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-white">Settings</h1>
        </div>
      </header>
      <main className="max-w-3xl mx-auto p-4 space-y-6">
        <section className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-gray-300 mb-4">API Keys</h2>
          <div className="space-y-4">
            {(['groq', 'openai', 'gemini'] as LLMProvider[]).map((provider) => (
              <div key={provider}>
                <label className="block text-sm font-medium text-gray-400 mb-1 capitalize">
                  {provider} API Key
                </label>
                <div className="flex gap-2">
                  <input
                    type={visibleKeys[provider] ? 'text' : 'password'}
                    defaultValue={apiKeys[provider] || ''}
                    onBlur={(e) => handleSaveKey(provider, e.target.value)}
                    className="flex-1 bg-gray-700 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder={`Enter your ${provider} API key...`}
                  />
                  <button
                    onClick={() => toggleVisibility(provider)}
                    className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                  >
                    {visibleKeys[provider] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-gray-300 mb-4">Default Provider</h2>
          <select
            value={defaultProvider}
            onChange={(e) => setDefaultProvider(e.target.value as LLMProvider)}
            className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="groq">Groq</option>
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
          </select>
        </section>

        <section className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-gray-300 mb-4">Danger Zone</h2>
          <button
            onClick={() => {
              if (confirm('Are you sure you want to clear all settings?')) {
                clearAll();
              }
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Clear All Settings
          </button>
        </section>
      </main>
    </div>
  );
}