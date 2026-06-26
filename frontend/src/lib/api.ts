import axios, { AxiosError, AxiosInstance } from 'axios';
import { ApiResponse } from '@/types/api';
import { CreateChatRequest, CreateChatResponse, LLMProvider } from '@/types/agent';
import { WorkflowConfig, WorkflowTemplate, WorkflowRun } from '@/types/workflow';
import { SessionState } from '@/types/agent';
import { UploadedFile } from '@/types/file';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000,
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.message);
        return Promise.reject(error);
      }
    );
  }

  async createChat(request: CreateChatRequest): Promise<CreateChatResponse> {
    const response = await this.client.post<ApiResponse<CreateChatResponse>>('/api/chat', request);
    return response.data.data!;
  }

  async getSession(sessionId: string): Promise<SessionState> {
    const response = await this.client.get<ApiResponse<SessionState>>(`/api/sessions/${sessionId}`);
    return response.data.data!;
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.client.delete(`/api/sessions/${sessionId}`);
  }

  async getSessions(): Promise<SessionState[]> {
    const response = await this.client.get<ApiResponse<{ sessions: SessionState[] }>>('/api/sessions');
    return response.data.data?.sessions || [];
  }

  async uploadFile(file: File, onProgress?: (progress: number) => void): Promise<UploadedFile> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<ApiResponse<UploadedFile>>('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress((event.loaded / event.total) * 100);
        }
      },
    });

    return response.data.data!;
  }

  async getWorkflows(): Promise<WorkflowConfig[]> {
    const response = await this.client.get<ApiResponse<{ workflows: WorkflowConfig[] }>>('/api/workflows');
    return response.data.data?.workflows || [];
  }

  async getWorkflowTemplates(): Promise<WorkflowTemplate[]> {
    const response = await this.client.get<ApiResponse<{ templates: WorkflowTemplate[] }>>('/api/workflows/templates');
    return response.data.data?.templates || [];
  }

  async getWorkflowTemplate(templateId: string): Promise<WorkflowConfig> {
    const response = await this.client.get<ApiResponse<WorkflowConfig>>(`/api/workflows/templates/${templateId}`);
    return response.data.data!;
  }

  async createWorkflow(config: WorkflowConfig): Promise<WorkflowConfig> {
    const response = await this.client.post<ApiResponse<WorkflowConfig>>('/api/workflows', config);
    return response.data.data!;
  }

  async runWorkflow(workflowId: string, inputs: Record<string, any>): Promise<WorkflowRun> {
    const response = await this.client.post<ApiResponse<WorkflowRun>>(`/api/workflows/${workflowId}/run`, { inputs });
    return response.data.data!;
  }

  async getWorkflowRun(runId: string): Promise<WorkflowRun> {
    const response = await this.client.get<ApiResponse<WorkflowRun>>(`/api/runs/${runId}`);
    return response.data.data!;
  }

  async exportSession(sessionId: string, format: 'markdown' | 'json'): Promise<{ content: string; filename: string }> {
    const response = await this.client.get<ApiResponse<{ content: string; filename: string }>>(
      `/api/sessions/${sessionId}/export?format=${format}`
    );
    return response.data.data!;
  }

  async saveSessionMemory(sessionId: string): Promise<void> {
    await this.client.post(`/api/sessions/${sessionId}/memory`);
  }

  async getSessionContext(sessionId: string): Promise<any> {
    const response = await this.client.get(`/api/sessions/${sessionId}/context`);
    return response.data;
  }

  async healthCheck(): Promise<{ status: string; version: string; uptime: number }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const api = new ApiClient();
export default api;