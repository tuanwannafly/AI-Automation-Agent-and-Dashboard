import { create } from "zustand";
import { Message, LLMProvider, AgentEvent } from "@/types/agent";

interface AgentStore {
  messages: Message[];
  sessionId: string | null;
  currentStreamingText: string;
  isRunning: boolean;
  llmProvider: LLMProvider;
  selectedWorkflowId: string | null;

  addMessage: (message: Message) => void;
  updateLastMessage: (update: Partial<Message>) => void;
  setSessionId: (id: string) => void;
  appendStreamingToken: (token: string) => void;
  finalizeStreaming: () => void;
  setRunning: (running: boolean) => void;
  setLLMProvider: (provider: LLMProvider) => void;
  setWorkflow: (id: string | null) => void;
  handleAgentEvent: (event: AgentEvent) => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  messages: [],
  sessionId: null,
  currentStreamingText: "",
  isRunning: false,
  llmProvider: "groq",
  selectedWorkflowId: null,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  updateLastMessage: (update) =>
    set((state) => {
      const messages = [...state.messages];
      messages[messages.length - 1] = { ...messages[messages.length - 1], ...update };
      return { messages };
    }),

  setSessionId: (id) => set({ sessionId: id }),
  appendStreamingToken: (token) =>
    set((state) => ({ currentStreamingText: state.currentStreamingText + token })),
  finalizeStreaming: () => set({ currentStreamingText: "", isRunning: false }),
  setRunning: (running) => set({ isRunning: running }),
  setLLMProvider: (provider) => set({ llmProvider: provider }),
  setWorkflow: (id) => set({ selectedWorkflowId: id }),

  handleAgentEvent: (event) => {
    const { appendStreamingToken, updateLastMessage, finalizeStreaming } = get();
    switch (event.type) {
      case "STREAMING_TOKEN":
        if (event.token) appendStreamingToken(event.token);
        break;
      case "DONE":
        updateLastMessage({
          content: event.final_answer || get().currentStreamingText,
          reasoning: event.reasoning_chain,
          tokensUsed: event.total_tokens,
          timeTaken: event.total_time_ms,
          isStreaming: false,
        });
        finalizeStreaming();
        break;
      case "ERROR":
        updateLastMessage({ content: `❌ Error: ${event.message}`, isStreaming: false });
        set({ isRunning: false });
        break;
    }
  },
}));