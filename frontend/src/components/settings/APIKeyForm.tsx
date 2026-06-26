'use client';

import { useState } from 'react';
import { useSettingsStore } from '@/store/settingsStore';
import { LLMProvider } from '@/types/agent';
import { LLMTestConnection } from './LLMTestConnection';
import { Eye, EyeOff } from 'lucide-react';

interface APIKeyFormProps {
  provider: LLMProvider;
}

export function APIKeyForm({ provider }: APIKeyFormProps) {
  const { apiKeys, setApiKey } = useSettingsStore();
  const [visible, setVisible] = useState(false);
  const [value, setValue] = useState(apiKeys[provider] || '');

  const handleSave = () => {
    setApiKey(provider, value);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-400 mb-1 capitalize">
        {provider} API Key
      </label>
      <div className="flex gap-2 mb-2">
        <input
          type={visible ? 'text' : 'password'}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onBlur={handleSave}
          className="flex-1 bg-gray-700 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder={`Enter your ${provider} API key...`}
        />
        <button
          onClick={() => setVisible(!visible)}
          className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          {visible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </div>
      <LLMTestConnection provider={provider} apiKey={value} />
    </div>
  );
}