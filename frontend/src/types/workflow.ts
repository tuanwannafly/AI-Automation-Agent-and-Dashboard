export interface WorkflowConfig {
  id: string;
  name: string;
  description: string;
  version: string;
  steps: WorkflowStep[];
  inputs: WorkflowInput[];
  outputs?: WorkflowOutput[];
}

export interface WorkflowStep {
  id: string;
  name: string;
  type: 'tool' | 'condition' | 'loop' | 'output';
  toolName?: string;
  toolArgs?: Record<string, any>;
  condition?: string;
  loopOver?: string;
  outputVar?: string;
}

export interface WorkflowInput {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  defaultValue?: any;
  description?: string;
}

export interface WorkflowOutput {
  name: string;
  value: any;
}

export interface WorkflowRun {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  steps: WorkflowStepResult[];
  startedAt?: number;
  completedAt?: number;
  error?: string;
}

export interface WorkflowStepResult {
  stepId: string;
  stepName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  output?: any;
  error?: string;
  startedAt?: number;
  completedAt?: number;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  config: WorkflowConfig;
}