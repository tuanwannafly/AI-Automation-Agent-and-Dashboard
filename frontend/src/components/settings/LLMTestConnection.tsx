'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { WorkflowTemplate } from '@/types/workflow';
import { Check } from 'lucide-react';

interface LLMTestConnectionProps {
  provider: 'groq' | 'openai' | 'gemini';
  apiKey: string;
}

export function LLMTestConnection({ provider, apiKey }: LLMTestConnectionProps) {
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<'success' | 'error' | null>(null);

  const handleTest = async () => {
    if (!apiKey) {
      alert('Please enter an API key first');
      return;
    }

    setTesting(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      
      if (data.llmProviders && data.llmProviders[provider]) {
        setResult('success');
      } else {
        setResult('error');
      }
    } catch (err) {
      setResult('error');
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleTest}
        disabled={testing || !apiKey}
        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:cursor-not-allowed text-white text-sm rounded transition-colors"
      >
        {testing ? 'Testing...' : 'Test Connection'}
      </button>
      {result === 'success' && <Check className="w-4 h-4 text-green-400" />}
      {result === 'error' && (
        <span className="text-xs text-red-400">Failed</span>
      )}
    </div>
  );
}