'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { SessionState, Message } from '@/types/agent';
import { ArrowLeft, Download } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { StreamingText } from '@/components/chat/StreamingText';

export default function SessionDetailPage() {
  const params = useParams();
  const sessionId = params.id as string;
  const [session, setSession] = useState<SessionState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getSession(sessionId)
      .then(setSession)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [sessionId]);

  const handleExport = async (format: 'markdown' | 'json') => {
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
        <div className="text-gray-400">Loading session...</div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-red-400">{error || 'Session not found'}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <header className="border-b border-gray-700 bg-gray-800">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/sessions" className="p-2 hover:bg-gray-700 rounded transition-colors">
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </Link>
            <div>
              <h1 className="text-xl font-bold text-white">Session Details</h1>
              <p className="text-xs text-gray-500">{session.id}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleExport('markdown')}
              className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition-colors"
            >
              Export Markdown
            </button>
            <button
              onClick={() => handleExport('json')}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors"
            >
              Export JSON
            </button>
          </div>
        </div>
      </header>
      <main className="max-w-4xl mx-auto p-4">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-300 mb-3">Reasoning Chain</h2>
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 max-h-64 overflow-y-auto">
            {session.reasoningChain.length === 0 ? (
              <p className="text-gray-500 text-sm">No reasoning steps recorded</p>
            ) : (
              <div className="space-y-2">
                {session.reasoningChain.map((step, i) => (
                  <div key={step.id} className="text-sm">
                    <span className="text-purple-400 font-medium">[{i + 1}] </span>
                    <span className="text-gray-300">{step.type}: </span>
                    <span className="text-gray-400">{step.content.substring(0, 100)}{step.content.length > 100 ? '...' : ''}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-300 mb-3">Messages</h2>
          <div className="space-y-3">
            {session.messages.map((message: Message) => (
              <div
                key={message.id}
                className={`rounded-lg p-4 ${message.role === 'user' ? 'bg-purple-900/30 border border-purple-700' : 'bg-gray-800 border border-gray-700'}`}
              >
                <div className="text-xs text-gray-500 mb-1 capitalize">{message.role}</div>
                <StreamingText content={message.content} />
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}