'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { SessionState } from '@/types/agent';
import { MessageSquare, Trash2, Download, Eye } from 'lucide-react';
import Link from 'next/link';

export default function SessionsPage() {
  const [sessions, setSessions] = useState<SessionState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getSessions()
      .then(setSessions)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this session?')) return;
    try {
      await api.deleteSession(sessionId);
      setSessions(sessions.filter(s => s.id !== sessionId));
    } catch (err) {
      alert('Failed to delete session');
    }
  };

  const handleExport = async (sessionId: string, format: 'markdown' | 'json') => {
    try {
      const result = await api.exportSession(sessionId, format);
      const blob = new Blob([result.content], { type: format === 'json' ? 'application/json' : 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to export session');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-gray-400">Loading sessions...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <header className="border-b border-gray-700 bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-white">Session History</h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto p-4">
        {error ? (
          <div className="text-red-400 text-center py-8">{error}</div>
        ) : sessions.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No sessions yet. Start a chat to create one!</p>
            <Link href="/chat" className="text-purple-400 hover:underline mt-2 inline-block">
              Go to Chat
            </Link>
          </div>
        ) : (
          <div className="space-y-3 mt-4">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <MessageSquare className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-medium text-white">{session.id}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {session.messages.length} messages · {session.reasoningChain.length} reasoning steps
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    href={`/sessions/${session.id}`}
                    className="p-2 hover:bg-gray-700 rounded transition-colors"
                    title="View details"
                  >
                    <Eye className="w-4 h-4 text-gray-400" />
                  </Link>
                  <button
                    onClick={() => handleExport(session.id, 'markdown')}
                    className="p-2 hover:bg-gray-700 rounded transition-colors"
                    title="Export as Markdown"
                  >
                    <Download className="w-4 h-4 text-gray-400" />
                  </button>
                  <button
                    onClick={() => handleDelete(session.id)}
                    className="p-2 hover:bg-red-900/50 rounded transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}