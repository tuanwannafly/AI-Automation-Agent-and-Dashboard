'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { WorkflowTemplate } from '@/types/workflow';
import { FileText, Play, Upload } from 'lucide-react';

export default function WorkflowsPage() {
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getWorkflowTemplates()
      .then(setTemplates)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleUploadYAML = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.yaml,.yml';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:8000/api/workflows', {
          method: 'POST',
          body: formData,
        });
        const result = await response.json();
        alert(result.data ? 'Workflow uploaded successfully!' : 'Upload failed');
      } catch (err) {
        alert('Upload failed: ' + (err as Error).message);
      }
    };
    input.click();
  };

  const handleRunWorkflow = async (templateId: string) => {
    try {
      const config = await api.getWorkflowTemplate(templateId);
      const run = await api.runWorkflow(config.id, {});
      alert(`Workflow started! Run ID: ${run.id}`);
    } catch (err) {
      alert('Failed to run workflow: ' + (err as Error).message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-gray-400">Loading workflows...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <header className="border-b border-gray-700 bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">Workflow Gallery</h1>
          <button
            onClick={handleUploadYAML}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
          >
            <Upload className="w-4 h-4" />
            Upload YAML
          </button>
        </div>
      </header>
      <main className="max-w-7xl mx-auto p-4">
        {error ? (
          <div className="text-red-400 text-center py-8">{error}</div>
        ) : templates.length === 0 ? (
          <div className="text-gray-500 text-center py-8">No workflows available</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
            {templates.map((template) => (
              <div key={template.id} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-purple-400" />
                    <h3 className="text-lg font-semibold text-white">{template.name}</h3>
                  </div>
                  <span className="text-xs bg-gray-700 text-gray-400 px-2 py-1 rounded">
                    {template.category}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-4">{template.description}</p>
                <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                  <span>{template.config.steps.length} steps</span>
                  <span>v{template.config.version}</span>
                </div>
                <button
                  onClick={() => handleRunWorkflow(template.id)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                >
                  <Play className="w-4 h-4" />
                  Run Workflow
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}