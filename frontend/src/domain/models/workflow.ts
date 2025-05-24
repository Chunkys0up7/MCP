import { Node, Edge } from 'reactflow';

export type WorkflowExecutionStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export type ValidationSeverity = 'error' | 'warning' | 'info';

export interface ValidationError {
  type: string;
  message: string;
  nodeId: string;
  severity: ValidationSeverity;
  details?: Record<string, any>;
}

export interface ValidationRule {
  id: string;
  name: string;
  description: string;
  validate: (nodes: Node[], edges: Edge[]) => ValidationError[];
}

export interface WorkflowValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  timestamp: string;
}

export interface WorkflowStep {
  id: string;
  nodeId: string;
  status: WorkflowExecutionStatus;
  startTime?: string;
  endTime?: string;
  error?: string;
  result?: any;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: WorkflowExecutionStatus;
  startTime: string;
  endTime?: string;
  steps: WorkflowStep[];
  error?: string;
}

export interface WorkflowNode {
  id: string;
  type: string;
  data: {
    type: string;
    config?: {
      complexity?: number;
      estimatedDataSize?: number;
      [key: string]: any;
    };
    [key: string]: any;
  };
  position: { x: number; y: number };
}

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: Node<WorkflowNode>[];
  edges: Edge[];
  createdAt: string;
  updatedAt: string;
  lastExecuted?: string;
  executionCount: number;
  averageExecutionTime?: number;
  successRate?: number;
} 