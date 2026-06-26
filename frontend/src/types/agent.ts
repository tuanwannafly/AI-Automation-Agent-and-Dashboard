import { v4 as uuidv4 } from 'uuid';

export type LLMProvider = 'groq' | 'openai' | 'gemini';

export type AgentEventType = 
  | 'THINKING' 
  | 'TOOL_CALL' 
  | 'TOOL_RESULT' 
  | 'STREAMING_TOKEN' 
  | 'WORKFLOW_STEP' 
  | 'DONE' 
  | 'ERROR'
  | 'PONG';

export interface AgentEvent {
  type: AgentEventType;
  data: any;
  timestamp: number;
  id: string;
}

export interface ThinkingData {
  thought: string;
  duration?: number;
}

export interface ToolCallData {
  toolName: string;
  toolArgs: Record<string, any>;
  toolCallId: string;
}

export interface ToolResultData {
  toolCallId: string;
  toolName: string;
  result: any;
  isError?: boolean;
}

export interface WorkflowStepData {
  stepName: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  output?: any;
  error?: string;
}

export interface StreamingTokenData {
  token: string;
  isAssistant: boolean;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  reasoning?: ReasoningStep[];
  toolCalls?: ToolCallData[];
  toolResults?: ToolResultData[];
}

export interface ReasoningStep {
  id: string;
  type: 'thinking' | 'tool_call' | 'tool_result';
  content: string;
  data?: any;
  timestamp: number;
}

export interface SessionState {
  id: string;
  messages: Message[];
  reasoningChain: ReasoningStep[];
  isRunning: boolean;
  isStreaming: boolean;
  error: string | null;
  currentProvider: LLMProvider;
}

export interface CreateChatRequest {
  message: string;
  llmProvider?: LLMProvider;
  sessionContext?: any;
}

export interface CreateChatResponse {
  sessionId: string;
  message: Message;
}