'use client';

import { ReasoningStep, ToolResultData } from '@/types/agent';
import { FileText, AlertCircle } from 'lucide-react';

interface ToolResultCardProps {
  step: ReasoningStep;
  index: number;
}

export function ToolResultCard({ step, index }: ToolResultCardProps) {
  const data = step.data as ToolResultData;
  const isError = data?.isError;

  return (
    <div className={`${isError ? 'bg-red-900/30 border-red-700/50' : 'bg-green-900/30 border-green-700/50'} border rounded-lg p-3`}>
      <div className="flex items-center gap-2 mb-2">
        {isError ? (
          <AlertCircle className="w-4 h-4 text-red-400" />
        ) : (
          <FileText className="w-4 h-4 text-green-400" />
        )}
        <span className={`text-xs font-semibold ${isError ? 'text-red-400' : 'text-green-400'}`}>
          Step {index} · {isError ? 'Error' : 'Result'}
        </span>
      </div>
      <div className="text-sm text-gray-300">
        {isError ? (
          <p className="text-red-300">{data?.result || 'Unknown error'}</p>
        ) : (
          <pre className="text-xs bg-gray-900/50 rounded p-2 text-gray-400 overflow-auto max-h-40">
            {typeof data?.result === 'string' ? data.result : JSON.stringify(data?.result, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}