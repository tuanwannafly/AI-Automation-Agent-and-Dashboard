import { LLMProvider, Message, SessionState } from './agent';
import { WorkflowConfig, WorkflowRun, WorkflowTemplate } from './workflow';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface SessionResponse {
  session: SessionState;
}

export interface SessionsListResponse {
  sessions: SessionState[];
}

export interface WorkflowsListResponse {
  workflows: WorkflowConfig[];
}

export interface WorkflowTemplatesResponse {
  templates: WorkflowTemplate[];
}

export interface WorkflowRunResponse {
  run: WorkflowRun;
}

export interface UploadResponse {
  fileId: string;
  filename: string;
  size: number;
  status: 'uploaded' | 'indexed' | 'error';
  message?: string;
}

export interface ExportResponse {
  format: 'markdown' | 'json';
  content: string;
  filename: string;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  version: string;
  uptime: number;
  llmProviders: Record<LLMProvider, boolean>;
}