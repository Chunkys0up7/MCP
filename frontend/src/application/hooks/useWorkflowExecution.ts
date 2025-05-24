import { useState, useCallback, useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { workflowExecutionService } from '../../infrastructure/services/workflowExecutionService';
import {
  WorkflowExecutionState,
  WorkflowExecutionStatus,
  WorkflowStep
} from '../../domain/models/workflow';

export const useWorkflowExecution = (workflowId: string) => {
  const [state, setState] = useState<WorkflowExecutionState>({
    status: 'IDLE',
    progress: 0,
    totalSteps: 0,
    completedSteps: 0
  });

  const { lastMessage, sendMessage } = useWebSocket(`/ws/workflows/${workflowId}/execution`);

  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      handleExecutionUpdate(data);
    }
  }, [lastMessage]);

  const handleExecutionUpdate = (data: any) => {
    setState(prevState => ({
      ...prevState,
      status: data.status,
      progress: data.progress,
      currentStep: data.currentStep,
      error: data.error,
      totalSteps: data.totalSteps,
      completedSteps: data.completedSteps
    }));
  };

  const startExecution = useCallback(async () => {
    try {
      setState(prev => ({
        ...prev,
        status: 'RUNNING',
        progress: 0,
        error: undefined,
        startTime: new Date()
      }));

      await workflowExecutionService.startExecution(workflowId);
      sendMessage({ type: 'START_EXECUTION' });
    } catch (error) {
      setState(prev => ({
        ...prev,
        status: 'FAILED',
        error: {
          message: 'Failed to start execution',
          details: error instanceof Error ? error.message : String(error)
        }
      }));
    }
  }, [workflowId, sendMessage]);

  const stopExecution = useCallback(async () => {
    try {
      await workflowExecutionService.stopExecution(workflowId);
      sendMessage({ type: 'STOP_EXECUTION' });
      setState(prev => ({
        ...prev,
        status: 'FAILED',
        error: {
          message: 'Execution stopped by user'
        }
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: {
          message: 'Failed to stop execution',
          details: error instanceof Error ? error.message : String(error)
        }
      }));
    }
  }, [workflowId, sendMessage]);

  const resetExecution = useCallback(() => {
    setState({
      status: 'IDLE',
      progress: 0,
      totalSteps: 0,
      completedSteps: 0
    });
  }, []);

  return {
    ...state,
    startExecution,
    stopExecution,
    resetExecution
  };
}; 