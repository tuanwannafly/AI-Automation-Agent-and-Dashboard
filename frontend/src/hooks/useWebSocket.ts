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
  const pendingMessageRef = useRef<any>(null);
  const MAX_RETRIES = 5;
  const BASE_RECONNECT_DELAY = 1000;
  const PING_INTERVAL = 30000;
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const onConnectRef = useRef(onConnect);
  const onDisconnectRef = useRef(onDisconnect);
  const onErrorRef = useRef(onError);
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

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = apiUrl.replace(/^https?:\/\//, '');
    const wsUrl = `${wsProtocol}://${wsHost}/api/ws/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      retryCountRef.current = 0;
      wsRef.current = ws;
      startPingInterval(ws);
      onConnectRef.current?.();
      
      // Send pending message immediately after connect
      if (pendingMessageRef.current) {
        console.log('[useWebSocket] Sending pending message on open:', pendingMessageRef.current);
        ws.send(JSON.stringify(pendingMessageRef.current));
        pendingMessageRef.current = null;
      }
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
      onErrorRef.current?.('WebSocket connection error');
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      wsRef.current = null;
      
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
      
      onDisconnectRef.current?.();

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
  }, [sessionId, enabled, cleanup, startPingInterval, handleAgentEvent]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('[useWebSocket] Sending message via WebSocket:', message);
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.log('[useWebSocket] Queueing message, readyState:', wsRef.current?.readyState);
      pendingMessageRef.current = message;
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