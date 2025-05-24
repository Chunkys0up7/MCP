export type WorkflowExecutionStatus = 'IDLE' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface WorkflowStep {
  id: string;
  name: string;
  description?: string;
  type: 'LLM' | 'NOTEBOOK' | 'DATA' | 'INPUT' | 'OUTPUT';
  status: WorkflowExecutionStatus;
  progress: number;
  error?: {
    message: string;
    details?: string;
  };
}

export interface WorkflowExecutionState {
  status: WorkflowExecutionStatus;
  progress: number;
  currentStep?: WorkflowStep;
  error?: {
    message: string;
    details?: string;
  };
  startTime?: Date;
  endTime?: Date;
  totalSteps: number;
  completedSteps: number;
}

export interface WorkflowExecutionResult {
  status: WorkflowExecutionStatus;
  outputs?: Record<string, any>;
  error?: {
    message: string;
    details?: string;
  };
  executionTime: number;
  stepResults: Array<{
    stepId: string;
    status: WorkflowExecutionStatus;
    outputs?: Record<string, any>;
    error?: {
      message: string;
      details?: string;
    };
  }>;
} 