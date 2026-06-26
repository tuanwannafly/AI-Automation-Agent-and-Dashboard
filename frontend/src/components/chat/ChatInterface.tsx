"use client";

import { useState } from "react";
import { useAgentStore } from "@/store/agentStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { MessageList } from "./MessageList";
import { InputArea } from "./InputArea";
import { AgentPanel } from "../agent/AgentPanel";
import api from "@/lib/api";
import { v4 as uuidv4 } from "uuid";

export function ChatInterface() {
  const {
    messages, sessionId, isRunning, llmProvider,
    addMessage, setSessionId, setRunning, handleAgentEvent,
  } = useAgentStore();

  const { status, setOnEvent } = useWebSocket(sessionId);
  const [agentEvents, setAgentEvents] = useState<any[]>([]);

  useEffect(() => {
    setOnEvent((event) => {
      handleAgentEvent(event);
      setAgentEvents((prev) => [...prev, event]);
    });
  }, [setOnEvent, handleAgentEvent]);

  const handleSend = async (text: string, fileIds: string[]) => {
    if (!text.trim() || isRunning) return;

    addMessage({ id: uuidv4(), role: "user", content: text, timestamp: Date.now() });
    addMessage({ id: uuidv4(), role: "assistant", content: "", timestamp: Date.now(), isStreaming: true });

    setRunning(true);
    setAgentEvents([]);

    try {
      const response = await api.post("/api/chat", {
        message: text,
        file_ids: fileIds,
        llm_provider: llmProvider,
      });
      setSessionId(response.data.session_id);
    } catch (error) {
      setRunning(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      <div className="flex flex-col flex-1 min-w-0">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
          <h1 className="font-semibold text-lg tracking-tight">AI Agent</h1>
          <div className="flex items-center gap-3">
            <select
              value={llmProvider}
              onChange={(e) => useAgentStore.getState().setLLMProvider(e.target.value as any)}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-1 text-sm"
            >
              <option value="groq">Groq</option>
              <option value="openai">OpenAI</option>
              <option value="gemini">Gemini</option>
            </select>
            <span className={`text-xs px-2 py-1 rounded ${
              status === "connected" ? "bg-green-900 text-green-400" :
              status === "connecting" ? "bg-yellow-900 text-yellow-400" :
              "bg-red-900 text-red-400"
            }`}>
              {status}
            </span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <MessageList messages={messages} />
        </div>

        <InputArea onSend={handleSend} disabled={isRunning} />
      </div>

      <AgentPanel events={agentEvents} />
    </div>
  );
}