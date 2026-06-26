'use client';

import { ReasoningStep } from '@/types/agent';
import { Activity } from 'lucide-react';

interface ExecutionTimelineProps {
  steps: ReasoningStep[];
}

export function ExecutionTimeline({ steps }: ExecutionTimelineProps) {
  const toolSteps = steps.filter(s => s.type === 'tool_call' || s.type === 'tool_result');

  if (toolSteps.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-gray-700">
      <div className="flex items-center gap-2 mb-3">
        <Activity className="w-4 h-4 text-gray-400" />
        <span className="text-xs font-semibold text-gray-400">Execution Timeline</span>
      </div>
      <div className="space-y-2">
        {toolSteps.map((step, index) => (
          <div key={step.id} className="flex items-center gap-2 text-xs">
            <div className={`w-2 h-2 rounded-full ${
              step.type === 'tool_call' ? 'bg-blue-400' : 'bg-green-400'
            }`} />
            <span className="text-gray-400">
              {step.type === 'tool_call' ? 'Call' : 'Result'}: {step.content.substring(0, 30)}...
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}