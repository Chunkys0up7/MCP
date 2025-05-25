import { useState, useCallback, useEffect } from 'react';
import { Node, Edge } from 'reactflow';
import { errorHandlingService, WorkflowError } from '../../infrastructure/services/errorHandlingService';

export const useErrorHandling = (nodes: Node[], edges: Edge[]) => {
  const [errors, setErrors] = useState<WorkflowError[]>([]);
  const [errorStats, setErrorStats] = useState(errorHandlingService.getErrorStats());

  const handleError = useCallback((error: Omit<WorkflowError, 'id' | 'timestamp' | 'retryCount' | 'status'>) => {
    const newError = errorHandlingService.handleError(error);
    setErrors(prev => [...prev, newError]);
    setErrorStats(errorHandlingService.getErrorStats());
    return newError;
  }, []);

  const retryError = useCallback(async (errorId: string, retryFn: () => Promise<any>) => {
    const success = await errorHandlingService.retryError(errorId, retryFn);
    setErrors(errorHandlingService.getActiveErrors());
    setErrorStats(errorHandlingService.getErrorStats());
    return success;
  }, []);

  const resolveError = useCallback((errorId: string) => {
    errorHandlingService.resolveError(errorId);
    setErrors(errorHandlingService.getActiveErrors());
    setErrorStats(errorHandlingService.getErrorStats());
  }, []);

  const ignoreError = useCallback((errorId: string) => {
    errorHandlingService.ignoreError(errorId);
    setErrors(errorHandlingService.getActiveErrors());
    setErrorStats(errorHandlingService.getErrorStats());
  }, []);

  const getErrorsForNode = useCallback((nodeId: string) => {
    return errorHandlingService.getErrorsByNode(nodeId);
  }, []);

  const getErrorsByType = useCallback((type: WorkflowError['type']) => {
    return errorHandlingService.getErrorsByType(type);
  }, []);

  // Update error stats periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setErrorStats(errorHandlingService.getErrorStats());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return {
    errors,
    errorStats,
    handleError,
    retryError,
    resolveError,
    ignoreError,
    getErrorsForNode,
    getErrorsByType
  };
}; 