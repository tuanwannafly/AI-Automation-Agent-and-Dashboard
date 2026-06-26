'use client';

import { useState } from 'react';
import { WorkflowInput } from '@/types/workflow';
import { Play } from 'lucide-react';

interface WorkflowInputsFormProps {
  inputs: WorkflowInput[];
  onSubmit: (values: Record<string, any>) => void;
  loading?: boolean;
}

export function WorkflowInputsForm({ inputs, onSubmit, loading = false }: WorkflowInputsFormProps) {
  const [values, setValues] = useState<Record<string, any>>({
    ...inputs.reduce((acc, input) => {
      acc[input.name] = input.defaultValue ?? '';
      return acc;
    }, {} as Record<string, any>)
  });

  const handleChange = (name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(values);
  };

  const renderInput = (input: WorkflowInput) => {
    const value = values[input.name];

    switch (input.type) {
      case 'boolean':
        return (
          <input
            type="checkbox"
            checked={value || false}
            onChange={(e) => handleChange(input.name, e.target.checked)}
            className="w-4 h-4"
          />
        );
      case 'number':
        return (
          <input
            type="number"
            value={value || ''}
            onChange={(e) => handleChange(input.name, parseFloat(e.target.value))}
            className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        );
      default:
        return (
          <input
            type="text"
            value={value || ''}
            onChange={(e) => handleChange(input.name, e.target.value)}
            className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder={input.description}
          />
        );
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {inputs.map((input) => (
        <div key={input.name}>
          <label className="block text-sm font-medium text-gray-400 mb-1">
            {input.name} {input.required && <span className="text-red-400">*</span>}
          </label>
          {renderInput(input)}
        </div>
      ))}
      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors"
      >
        <Play className="w-4 h-4" />
        {loading ? 'Running...' : 'Run Workflow'}
      </button>
    </form>
  );
}