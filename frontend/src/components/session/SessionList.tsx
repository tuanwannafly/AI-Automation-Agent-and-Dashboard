'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { SessionState } from '@/types/agent';
import { Search } from 'lucide-react';

interface SessionListProps {
  onSelectSession: (sessionId: string) => void;
}

export function SessionList({ onSelectSession }: SessionListProps) {
  const [sessions, setSessions] = useState<SessionState[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSessions()
      .then(setSessions)
      .finally(() => setLoading(false));
  }, []);

  const filteredSessions = sessions.filter((session) =>
    session.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    session.messages.some(m => m.content.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return <div className="text-gray-500 text-sm">Loading sessions...</div>;
  }

  return (
    <div>
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search sessions..."
          className="w-full bg-gray-700 text-white rounded-lg pl-10 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
      </div>
      <div className="space-y-2">
        {filteredSessions.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-8">No sessions found</div>
        ) : (
          filteredSessions.map((session) => (
            <button
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className="w-full text-left p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <div className="text-sm font-medium text-gray-300 truncate">{session.id}</div>
              <div className="text-xs text-gray-500 mt-1">
                {session.messages.length} messages · {session.reasoningChain.length} steps
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}