export type AgentEventType =
  | "THINKING"
  | "TOOL_CALL"
  | "TOOL_RESULT"
  | "CODE_EXECUTING"
  | "CODE_RESULT"
  | "STREAMING_TOKEN"
  | "WORKFLOW_STEP"
  | "DONE"
  | "ERROR"
  | "PONG";

export interface AgentEvent {
  type: AgentEventType;
  content?: string;
  step?: number;
  tool?: string;
  input?: Record<string, unknown>;
  output?: string;
  duration_ms?: number;
  token?: string;
  step_id?: string;
  description?: string;
  final_answer?: string;
  reasoning_chain?: ReasoningStep[];
  total_tokens?: number;
  total_time_ms?: number;
  outputs?: Record<string, unknown>;
  message?: string;
  recoverable?: boolean;
}

export interface ReasoningStep {
  type: "THINKING" | "TOOL_USE" | "DONE";
  content: string;
  tool?: string;
  result_preview?: string;
  step?: number;
}

export type LLMProvider = "groq" | "openai" | "gemini";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  reasoning?: ReasoningStep[];
  isStreaming?: boolean;
  tokensUsed?: number;
  timeTaken?: number;
}