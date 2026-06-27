'use client';

import { useEffect, useState } from 'react';
import { useAgentStore } from '@/store/agentStore';
import { useFileUploadStore } from '@/store/fileUploadStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Message } from '@/types/agent';
import { v4 as uuidv4 } from 'uuid';
import api from '@/lib/api';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';

interface ChatInterfaceProps {
  initialSessionId?: string;
}

export function ChatInterface({ initialSessionId }: ChatInterfaceProps) {
  const { sessionId, messages, isRunning, isStreaming, setIsRunning, addMessage, setSessionId, setError } = useAgentStore();
  const files = useFileUploadStore((state) => state.files);
  const [localSessionId, setLocalSessionId] = useState<string>(initialSessionId || '');
  
  const effectiveSessionId = sessionId || localSessionId;
  const wsEnabled = !!effectiveSessionId && effectiveSessionId.trim() !== '';

  const { isConnected, sendMessage } = useWebSocket({
    sessionId: effectiveSessionId,
    enabled: wsEnabled,
    onConnect: () => console.log('WebSocket connected'),
    onDisconnect: () => {
      console.log('WebSocket disconnected');
      setIsRunning(false);
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
      setError(error);
      setIsRunning(false);
    }
  });

  const handleSend = async (content: string) => {
    console.log('[ChatInterface] Sending message:', content);
    
    // Only send file ids for uploads that completed successfully; these scope the
    // RAG context to the current conversation so old documents don't leak in.
    const fileIds = files
      .filter((f) => f.status === 'indexed' || f.status === 'uploaded')
      .map((f) => f.id);

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: Date.now()
    };

    addMessage(userMessage);
    setError(null);
    setIsRunning(true);

    try {
      if (!effectiveSessionId) {
        // First message: bootstrap one session via HTTP, then connect WS + send
        console.log('[ChatInterface] Bootstrapping new session via API...');
        const response = await api.createChat({
          message: content,
        });

        const newSessionId = response.sessionId;
        console.log('[ChatInterface] Setting session ID:', newSessionId);
        setSessionId(newSessionId);
        setLocalSessionId(newSessionId);

        // WS will connect on re-render; the message is queued until it opens
        sendMessage({ type: 'CHAT', content, fileIds });
      } else {
        // Subsequent messages: send directly over the existing WebSocket
        console.log('[ChatInterface] Sending via existing WebSocket:', content);
        sendMessage({ type: 'CHAT', content, fileIds });
      }
      // NOTE: isRunning is cleared by the backend's DONE/ERROR events via the store
    } catch (error: any) {
      console.error('[ChatInterface] Error:', error);
      setError(error?.message || 'Failed to send message');
      setIsRunning(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-400">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <span className="text-sm text-gray-500">
          Session: {sessionId || localSessionId || 'Not started'}
        </span>
      </div>
      <MessageList messages={messages} />
      <InputArea onSend={handleSend} disabled={isRunning || isStreaming} />
    </div>
  );
}