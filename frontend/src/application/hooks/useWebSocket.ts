import { useEffect, useCallback, useState } from 'react';
import { websocketService, WebSocketMessage, ExecutionUpdate, ResourceUpdate } from '../../infrastructure/services/websocketService';

interface WebSocketState {
  isConnected: boolean;
  executionUpdates: Map<string, ExecutionUpdate>;
  resourceUpdates: ResourceUpdate[];
  errors: string[];
}

export const useWebSocket = (workflowId: string) => {
  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    executionUpdates: new Map(),
    resourceUpdates: [],
    errors: [],
  });

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'execution_update':
        setState(prev => ({
          ...prev,
          executionUpdates: new Map(prev.executionUpdates).set(
            message.payload.nodeId,
            message.payload as ExecutionUpdate
          ),
        }));
        break;

      case 'resource_update':
        setState(prev => ({
          ...prev,
          resourceUpdates: [...prev.resourceUpdates, message.payload as ResourceUpdate].slice(-100), // Keep last 100 updates
        }));
        break;

      case 'error':
        setState(prev => ({
          ...prev,
          errors: [...prev.errors, message.payload].slice(-10), // Keep last 10 errors
        }));
        break;

      case 'status':
        setState(prev => ({
          ...prev,
          isConnected: message.payload.connected,
        }));
        break;
    }
  }, []);

  useEffect(() => {
    const unsubscribe = websocketService.subscribe(handleMessage);

    // Subscribe to workflow updates
    websocketService.send({
      type: 'status',
      payload: { workflowId },
      timestamp: Date.now(),
    });

    return () => {
      unsubscribe();
    };
  }, [workflowId, handleMessage]);

  const getNodeStatus = useCallback((nodeId: string) => {
    return state.executionUpdates.get(nodeId);
  }, [state.executionUpdates]);

  const getLatestResourceUpdate = useCallback(() => {
    return state.resourceUpdates[state.resourceUpdates.length - 1];
  }, [state.resourceUpdates]);

  const clearErrors = useCallback(() => {
    setState(prev => ({ ...prev, errors: [] }));
  }, []);

  return {
    isConnected: state.isConnected,
    getNodeStatus,
    getLatestResourceUpdate,
    errors: state.errors,
    clearErrors,
  };
}; 