'use client';

import { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { WorkflowConfig } from '@/types/workflow';
import { Save, X } from 'lucide-react';

interface YAMLEditorProps {
  yamlContent: string;
  onSave?: (content: string) => void;
  onClose?: () => void;
  readOnly?: boolean;
}

export function YAMLEditor({ yamlContent, onSave, onClose, readOnly = false }: YAMLEditorProps) {
  const [content, setContent] = useState(yamlContent);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setContent(yamlContent);
    setHasChanges(false);
  }, [yamlContent]);

  const handleChange = (value?: string) => {
    if (value) {
      setContent(value);
      setHasChanges(value !== yamlContent);
    }
  };

  const handleSave = () => {
    onSave?.(content);
    setHasChanges(false);
  };

  return (
    <div className="flex flex-col h-full bg-gray-900">
      <div className="flex items-center justify-between p-3 border-b border-gray-700 bg-gray-800">
        <h3 className="text-sm font-semibold text-gray-300">YAML Editor</h3>
        <div className="flex items-center gap-2">
          {hasChanges && (
            <button
              onClick={handleSave}
              className="flex items-center gap-1 px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded transition-colors"
            >
              <Save className="w-3 h-3" />
              Save
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-700 rounded transition-colors"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>
      </div>
      <Editor
        height="100%"
        language="yaml"
        value={content}
        onChange={handleChange}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          readOnly: readOnly,
        }}
      />
    </div>
  );
}