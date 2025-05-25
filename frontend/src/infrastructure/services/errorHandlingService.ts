import { Node, Edge } from 'reactflow';
import { WorkflowExecutionStatus } from '../../domain/models/workflow';

export interface ErrorDetails {
  message: string;
  code?: string;
  stack?: string;
  context?: Record<string, any>;
  lastRetryError?: string;
}

export interface WorkflowError {
  id: string;
  type: 'node-error' | 'step-error' | 'workflow-error';
  message: string;
  severity: 'error' | 'warning' | 'info';
  nodeId?: string;
  stepId?: string;
  timestamp: string;
  details?: ErrorDetails;
  retryCount: number;
  maxRetries: number;
  status: 'active' | 'resolved' | 'ignored';
}

export interface RetryStrategy {
  maxRetries: number;
  backoffMs: number;
  maxBackoffMs: number;
}

class ErrorHandlingService {
  private errors: WorkflowError[] = [];
  private defaultRetryStrategy: RetryStrategy = {
    maxRetries: 3,
    backoffMs: 1000,
    maxBackoffMs: 10000
  };

  handleError(error: Omit<WorkflowError, 'id' | 'timestamp' | 'retryCount' | 'status'>): WorkflowError {
    const newError: WorkflowError = {
      ...error,
      id: `error-${Date.now()}`,
      timestamp: new Date().toISOString(),
      retryCount: 0,
      status: 'active'
    };

    this.errors.push(newError);
    return newError;
  }

  async retryError(errorId: string, retryFn: () => Promise<any>): Promise<boolean> {
    const error = this.errors.find(e => e.id === errorId);
    if (!error || error.status !== 'active') return false;

    if (error.retryCount >= error.maxRetries) {
      error.status = 'resolved';
      return false;
    }

    const backoff = Math.min(
      this.defaultRetryStrategy.backoffMs * Math.pow(2, error.retryCount),
      this.defaultRetryStrategy.maxBackoffMs
    );

    await new Promise(resolve => setTimeout(resolve, backoff));

    try {
      await retryFn();
      error.status = 'resolved';
      return true;
    } catch (retryError) {
      error.retryCount++;
      error.details = {
        ...error.details,
        message: error.details?.message || error.message,
        lastRetryError: retryError instanceof Error ? retryError.message : String(retryError)
      };
      return false;
    }
  }

  resolveError(errorId: string): void {
    const error = this.errors.find(e => e.id === errorId);
    if (error) {
      error.status = 'resolved';
    }
  }

  ignoreError(errorId: string): void {
    const error = this.errors.find(e => e.id === errorId);
    if (error) {
      error.status = 'ignored';
    }
  }

  getActiveErrors(): WorkflowError[] {
    return this.errors.filter(e => e.status === 'active');
  }

  getErrorsByNode(nodeId: string): WorkflowError[] {
    return this.errors.filter(e => e.nodeId === nodeId);
  }

  getErrorsByType(type: WorkflowError['type']): WorkflowError[] {
    return this.errors.filter(e => e.type === type);
  }

  clearErrors(): void {
    this.errors = [];
  }

  setRetryStrategy(strategy: Partial<RetryStrategy>): void {
    this.defaultRetryStrategy = {
      ...this.defaultRetryStrategy,
      ...strategy
    };
  }

  getErrorStats(): {
    total: number;
    active: number;
    resolved: number;
    ignored: number;
    byType: Record<WorkflowError['type'], number>;
    bySeverity: Record<WorkflowError['severity'], number>;
  } {
    const stats = {
      total: this.errors.length,
      active: 0,
      resolved: 0,
      ignored: 0,
      byType: {
        'node-error': 0,
        'step-error': 0,
        'workflow-error': 0
      },
      bySeverity: {
        error: 0,
        warning: 0,
        info: 0
      }
    };

    this.errors.forEach(error => {
      stats[error.status]++;
      stats.byType[error.type]++;
      stats.bySeverity[error.severity]++;
    });

    return stats;
  }
}

export const errorHandlingService = new ErrorHandlingService(); 