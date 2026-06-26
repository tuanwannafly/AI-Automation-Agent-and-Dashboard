"use client";

import { AgentEvent } from "@/types/agent";
import { Brain, Zap } from "lucide-react";
import { useState } from "react";

interface Props {
  events: AgentEvent[];
}

export function AgentPanel({ events }: Props) {
  const [collapsed, setCollapsed] = useState(false);

  const relevantEvents = events.filter(
    (e) => ["THINKING", "TOOL_CALL", "TOOL_RESULT", "WORKFLOW_STEP", "DONE"].includes(e.type)
  );

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="w-10 border-l border-gray-800 flex items-center justify-center hover:bg-gray-900 transition-colors"
      >
        <span className="text-gray-400">▶</span>
      </button>
    );
  }

  return (
    <div className="w-80 border-l border-gray-800 flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Brain size={16} className="text-violet-400" />
          <span className="text-sm font-medium">Thought Process</span>
        </div>
        <button onClick={() => setCollapsed(true)} className="text-gray-500 hover:text-gray-300">
          <span>◀</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {relevantEvents.length === 0 && (
          <p className="text-xs text-gray-600 text-center mt-8">
            Reasoning steps will appear here during agent execution
          </p>
        )}

        {relevantEvents.map((event, i) => (
          <div key={i}>
            {event.type === "THINKING" && (
              <div className="flex gap-2 p-2 rounded-md bg-gray-900/50">
                <Brain size={14} className="text-violet-400 mt-0.5 shrink-0" />
                <p className="text-xs text-gray-300">{event.content}</p>
              </div>
            )}
            {event.type === "TOOL_CALL" && (
              <div className="p-2 rounded-md bg-blue-900/20 border border-blue-800/40">
                <p className="text-xs text-blue-400 font-medium">Using: {event.tool}</p>
              </div>
            )}
            {event.type === "TOOL_RESULT" && (
              <div className="p-2 rounded-md bg-green-900/20 border border-green-800/40">
                <p className="text-xs text-green-400 font-medium">Result from {event.tool}</p>
                <p className="text-xs text-gray-400 mt-1 truncate">{event.output?.slice(0, 100)}</p>
              </div>
            )}
            {event.type === "DONE" && (
              <div className="flex gap-2 p-2 rounded-md bg-green-900/20 border border-green-800/40">
                <Zap size={14} className="text-green-400 mt-0.5 shrink-0" />
                <div className="text-xs">
                  <p className="text-green-400 font-medium">Completed</p>
                  {event.total_time_ms && (
                    <p className="text-gray-400">{(event.total_time_ms / 1000).toFixed(1)}s · {event.total_tokens} tokens</p>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}