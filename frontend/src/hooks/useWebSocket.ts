import { useEffect, useRef, useCallback } from 'react';
import { useAgentStore } from '@/store/agentStore';
import { AgentEvent } from '@/types/agent';

interface UseWebSocketOptions {
  sessionId: string | null;
  enabled?: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: string) => void;
}

export function useWebSocket({ 
  sessionId, 
  enabled = true,
  onConnect,
  onDisconnect,
  onError 
}: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef(0);
  const MAX_RETRIES = 5;
  const BASE_RECONNECT_DELAY = 1000;
  const PING_INTERVAL = 30000;
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const handleAgentEvent = useAgentStore((state) => state.handleAgentEvent);

  const cleanup = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const startPingInterval = useCallback((ws: WebSocket) => {
    pingIntervalRef.current = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'PING' }));
      }
    }, PING_INTERVAL);
  }, []);

  const connect = useCallback(() => {
    if (!sessionId || !enabled) return;

    cleanup();

    const wsUrl = `ws://localhost:8000/ws/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      retryCountRef.current = 0;
      wsRef.current = ws;
      startPingInterval(ws);
      onConnect?.();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'PONG') {
          return;
        }

        const agentEvent: AgentEvent = {
          type: data.type as AgentEvent['type'],
          data: data.data,
          timestamp: data.timestamp || Date.now(),
          id: data.id || `evt_${Date.now()}`
        };

        handleAgentEvent(agentEvent);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.('WebSocket connection error');
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      wsRef.current = null;
      
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
      
      onDisconnect?.();

      if (!event.wasClean && retryCountRef.current < MAX_RETRIES) {
        const delay = BASE_RECONNECT_DELAY * Math.pow(2, retryCountRef.current);
        console.log(`Reconnecting in ${delay}ms...`);
        
        reconnectTimeoutRef.current = setTimeout(() => {
          retryCountRef.current += 1;
          connect();
        }, delay);
      }
    };

    wsRef.current = ws;
  }, [sessionId, enabled, cleanup, startPingInterval, handleAgentEvent, onConnect, onDisconnect, onError]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();
    return cleanup;
  }, [connect, cleanup]);

  return {
    sendMessage,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
    isConnecting: wsRef.current?.readyState === WebSocket.CONNECTING,
    reconnect: connect
  };
}