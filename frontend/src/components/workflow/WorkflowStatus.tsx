'use client';

import { WorkflowRun } from '@/types/workflow';
import { Activity, CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface WorkflowStatusProps {
  run: WorkflowRun | null;
}

export function WorkflowStatus({ run }: WorkflowStatusProps) {
  if (!run) return null;

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-semibold text-white">Workflow Execution</h3>
        </div>
        <div className="flex items-center gap-2">
          {run.status === 'running' && (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
              <span className="text-sm text-blue-400">Running...</span>
            </>
          )}
          {run.status === 'completed' && (
            <>
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span className="text-sm text-green-400">Completed</span>
            </>
          )}
          {run.status === 'failed' && (
            <>
              <XCircle className="w-4 h-4 text-red-400" />
              <span className="text-sm text-red-400">Failed</span>
            </>
          )}
        </div>
      </div>
      <div className="space-y-2">
        {run.steps.map((step) => (
          <div
            key={step.stepId}
            className="flex items-center justify-between p-2 bg-gray-900/50 rounded"
          >
            <span className="text-sm text-gray-300">{step.stepName}</span>
            <div className="flex items-center gap-2">
              {step.status === 'running' && (
                <Loader2 className="w-3 h-3 animate-spin text-blue-400" />
              )}
              {step.status === 'completed' && (
                <CheckCircle className="w-3 h-3 text-green-400" />
              )}
              {step.status === 'failed' && (
                <XCircle className="w-3 h-3 text-red-400" />
              )}
              {step.status === 'pending' && (
                <span className="text-xs text-gray-500">Pending</span>
              )}
              {step.status === 'skipped' && (
                <span className="text-xs text-gray-500">Skipped</span>
              )}
            </div>
          </div>
        ))}
      </div>
      {run.error && (
        <div className="mt-3 p-2 bg-red-900/30 border border-red-700/50 rounded text-sm text-red-300">
          {run.error}
        </div>
      )}
    </div>
  );
}