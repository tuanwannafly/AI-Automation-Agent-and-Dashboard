'use client';

import { ReasoningStep, ToolCallData } from '@/types/agent';
import { Wrench } from 'lucide-react';

interface ToolCallCardProps {
  step: ReasoningStep;
  index: number;
}

export function ToolCallCard({ step, index }: ToolCallCardProps) {
  const data = step.data as ToolCallData;

  return (
    <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-2">
        <Wrench className="w-4 h-4 text-blue-400" />
        <span className="text-xs font-semibold text-blue-400">
          Step {index} · Tool Call
        </span>
      </div>
      <div className="space-y-2">
        <div className="text-sm font-medium text-blue-300">{data?.toolName}</div>
        {data?.toolArgs && (
          <pre className="text-xs bg-gray-900/50 rounded p-2 text-gray-400 overflow-auto">
            {JSON.stringify(data.toolArgs, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}