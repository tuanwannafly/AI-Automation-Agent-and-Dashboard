'use client';

import { WorkflowConfig } from '@/types/workflow';
import { ChevronDown } from 'lucide-react';
import { useState } from 'react';

interface WorkflowSelectorProps {
  workflows: WorkflowConfig[];
  selectedWorkflow?: WorkflowConfig;
  onSelect: (workflow: WorkflowConfig) => void;
}

export function WorkflowSelector({ workflows, selectedWorkflow, onSelect }: WorkflowSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
      >
        <span className="text-sm text-gray-300">
          {selectedWorkflow?.name || 'Select a workflow...'}
        </span>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="absolute w-full mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
          {workflows.length === 0 ? (
            <div className="px-4 py-3 text-sm text-gray-500">No workflows available</div>
          ) : (
            workflows.map((workflow) => (
              <button
                key={workflow.id}
                onClick={() => {
                  onSelect(workflow);
                  setIsOpen(false);
                }}
                className={`w-full px-4 py-3 text-left hover:bg-gray-700 first:rounded-t-lg last:rounded-b-lg transition-colors ${
                  selectedWorkflow?.id === workflow.id ? 'bg-gray-700' : ''
                }`}
              >
                <div className="text-sm text-gray-300">{workflow.name}</div>
                <div className="text-xs text-gray-500">{workflow.description}</div>
              </button>
            ))
          )}
        </div>
      )}
      {isOpen && (
        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
      )}
    </div>
  );
}