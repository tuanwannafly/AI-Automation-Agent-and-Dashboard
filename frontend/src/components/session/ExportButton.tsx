'use client';

import { useState } from 'react';
import api from '@/lib/api';
import { Download } from 'lucide-react';

interface ExportButtonProps {
  sessionId: string;
  format?: 'markdown' | 'json';
}

export function ExportButton({ sessionId, format = 'markdown' }: ExportButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const result = await api.exportSession(sessionId, format);
      const blob = new Blob([result.content], { 
        type: format === 'json' ? 'application/json' : 'text/markdown' 
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
      alert('Failed to export session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={loading}
      className="flex items-center gap-2 px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white text-sm rounded-lg transition-colors disabled:cursor-not-allowed"
    >
      <Download className="w-4 h-4" />
      {loading ? 'Exporting...' : `Export ${format === 'json' ? 'JSON' : 'MD'}`}
    </button>
  );
}