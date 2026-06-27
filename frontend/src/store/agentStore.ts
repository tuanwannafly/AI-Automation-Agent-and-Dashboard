import { create } from 'zustand';
import { Message, ReasoningStep, AgentEvent, LLMProvider } from '@/types/agent';

interface AgentStore {
  sessionId: string | null;
  messages: Message[];
  reasoningChain: ReasoningStep[];
  isRunning: boolean;
  isStreaming: boolean;
  error: string | null;
  currentProvider: LLMProvider;
  
  setSessionId: (sessionId: string) => void;
  addMessage: (message: Message) => void;
  addReasoningStep: (step: ReasoningStep) => void;
  handleAgentEvent: (event: AgentEvent) => void;
  setIsRunning: (isRunning: boolean) => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setError: (error: string | null) => void;
  setProvider: (provider: LLMProvider) => void;
  clearSession: () => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  sessionId: null,
  messages: [],
  reasoningChain: [],
  isRunning: false,
  isStreaming: false,
  error: null,
  currentProvider: 'groq',
  
  setSessionId: (sessionId) => set({ sessionId }),
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  
  addReasoningStep: (step) => set((state) => ({
    reasoningChain: [...state.reasoningChain, step]
  })),
  
  handleAgentEvent: (event) => {
    const state = get();
    
    switch (event.type) {
      case 'THINKING':
        set((state) => ({
          reasoningChain: [
            ...state.reasoningChain,
            {
              id: event.id,
              type: 'thinking',
              content: event.data.thought,
              timestamp: event.timestamp
            }
          ]
        }));
        break;
        
      case 'TOOL_CALL':
        set((state) => ({
          reasoningChain: [
            ...state.reasoningChain,
            {
              id: event.id,
              type: 'tool_call',
              content: `Calling ${event.data.toolName}`,
              data: event.data,
              timestamp: event.timestamp
            }
          ]
        }));
        break;
        
      case 'TOOL_RESULT':
        set((state) => ({
          reasoningChain: [
            ...state.reasoningChain,
            {
              id: event.id,
              type: 'tool_result',
              content: JSON.stringify(event.data.result),
              data: event.data,
              timestamp: event.timestamp
            }
          ]
        }));
        break;
        
      case 'STREAMING_TOKEN':
        const { messages } = state;
        const lastMessage = messages[messages.length - 1];
        
        if (lastMessage && lastMessage.role === 'assistant') {
          set((state) => ({
            messages: state.messages.map((msg, idx) => 
              idx === messages.length - 1
                ? { ...msg, content: msg.content + event.data.token }
                : msg
            ),
            isStreaming: true
          }));
        } else {
          const newAssistantMessage: Message = {
            id: event.id,
            role: 'assistant',
            content: event.data.token,
            timestamp: event.timestamp
          };
          set((state) => ({
            messages: [...state.messages, newAssistantMessage],
            isStreaming: true
          }));
        }
        break;
        
      case 'DONE':
        set({ isRunning: false, isStreaming: false });
        break;
        
      case 'ERROR':
        set({ error: event.data.message, isRunning: false, isStreaming: false });
        break;
    }
  },
  
  setIsRunning: (isRunning) => set({ isRunning }),
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  setError: (error) => set({ error }),
  setProvider: (provider) => set({ currentProvider: provider }),
  
  clearSession: () => set({
    sessionId: null,
    messages: [],
    reasoningChain: [],
    isRunning: false,
    isStreaming: false,
    error: null
  })
}));