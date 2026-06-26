import { useEffect, useRef, useCallback, useState } from "react";
import { AgentEvent } from "@/types/agent";

type WSStatus = "connecting" | "connected" | "disconnected" | "error";

export function useWebSocket(sessionId: string | null) {
  const ws = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<WSStatus>("disconnected");
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const reconnectTimer = useRef<NodeJS.Timeout>();
  const onEventRef = useRef<((event: AgentEvent) => void) | null>(null);

  const connect = useCallback(() => {
    if (!sessionId) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"}/ws/${sessionId}`;
    ws.current = new WebSocket(wsUrl);
    setStatus("connecting");

    ws.current.onopen = () => {
      setStatus("connected");
      const pingInterval = setInterval(() => {
        if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ type: "PING" }));
        }
      }, 30000);
      ws.current.addEventListener("close", () => clearInterval(pingInterval));
    };

    ws.current.onmessage = (e) => {
      const event: AgentEvent = JSON.parse(e.data);
      if (event.type === "PONG") return;
      setEvents((prev) => [...prev, event]);
      onEventRef.current?.(event);
    };

    ws.current.onclose = () => {
      setStatus("disconnected");
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    ws.current.onerror = () => setStatus("error");
  }, [sessionId]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      ws.current?.close();
    };
  }, [connect]);

  const setOnEvent = useCallback((handler: (event: AgentEvent) => void) => {
    onEventRef.current = handler;
  }, []);

  return { status, events, setOnEvent };
}