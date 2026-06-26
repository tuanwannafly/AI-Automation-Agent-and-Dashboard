'use client';

import { useEffect, useState } from 'react';
import { useAgentStore } from '@/store/agentStore';
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
  const { sessionId, messages, setIsRunning, setIsStreaming, addMessage, setSessionId } = useAgentStore();
  const [localSessionId, setLocalSessionId] = useState<string>(initialSessionId || '');

  const { isConnected } = useWebSocket({
    sessionId: sessionId || localSessionId,
    enabled: !!sessionId || !!localSessionId,
    onConnect: () => console.log('WebSocket connected'),
    onDisconnect: () => console.log('WebSocket disconnected'),
    onError: (error) => console.error('WebSocket error:', error)
  });

  const handleSend = async (content: string) => {
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: Date.now()
    };

    addMessage(userMessage);
    setIsRunning(true);

    try {
      const response = await api.createChat({
        message: content,
        sessionContext: sessionId ? { previousSessionId: sessionId } : undefined
      });

      if (!sessionId) {
        setSessionId(response.sessionId);
        setLocalSessionId(response.sessionId);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
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
      <InputArea onSend={handleSend} disabled={false} />
    </div>
  );
}