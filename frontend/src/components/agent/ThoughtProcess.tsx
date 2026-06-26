'use client';

import { ReasoningStep } from '@/types/agent';
import { Brain } from 'lucide-react';

interface ThoughtProcessProps {
  step: ReasoningStep;
  index: number;
}

export function ThoughtProcess({ step, index }: ThoughtProcessProps) {
  return (
    <div className="bg-violet-900/30 border border-violet-700/50 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-2">
        <Brain className="w-4 h-4 text-violet-400" />
        <span className="text-xs font-semibold text-violet-400">
          Step {index} · Thinking
        </span>
      </div>
      <p className="text-sm text-gray-300 whitespace-pre-wrap">{step.content}</p>
    </div>
  );
}