'use client';

import { useState } from 'react';
import { useAgentStore } from '@/store/agentStore';
import { ChevronLeft, ChevronRight, Brain, Wrench, FileText } from 'lucide-react';
import { ThoughtProcess } from './ThoughtProcess';
import { ToolCallCard } from './ToolCallCard';
import { ToolResultCard } from './ToolResultCard';
import { ExecutionTimeline } from './ExecutionTimeline';

interface AgentPanelProps {
  isOpen?: boolean;
  onToggle?: () => void;
}

export function AgentPanel({ isOpen = true, onToggle }: AgentPanelProps) {
  const { reasoningChain } = useAgentStore();
  const [localOpen, setLocalOpen] = useState(isOpen);

  const open = onToggle ? isOpen : localOpen;
  const toggle = onToggle || (() => setLocalOpen(!localOpen));

  return (
    <div className={`border-l border-gray-700 bg-gray-800 transition-all duration-300 ${open ? 'w-96' : 'w-12'}`}>
      <div className="flex items-center justify-between p-2 border-b border-gray-700">
        {open && <span className="text-sm font-semibold text-gray-300">Agent Reasoning</span>}
        <button
          onClick={toggle}
          className="p-1 hover:bg-gray-700 rounded transition-colors"
        >
          {open ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>
      {open && (
        <div className="overflow-y-auto p-4 space-y-3 max-h-[calc(100vh-80px)]">
          {reasoningChain.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <Brain className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No reasoning steps yet</p>
            </div>
          ) : (
            reasoningChain.map((step, index) => (
              <div key={step.id}>
                {step.type === 'thinking' && (
                  <ThoughtProcess step={step} index={index + 1} />
                )}
                {step.type === 'tool_call' && (
                  <ToolCallCard step={step} index={index + 1} />
                )}
                {step.type === 'tool_result' && (
                  <ToolResultCard step={step} index={index + 1} />
                )}
              </div>
            ))
          )}
          {reasoningChain.some(s => s.type === 'tool_call') && (
            <ExecutionTimeline steps={reasoningChain} />
          )}
        </div>
      )}
    </div>
  );
}