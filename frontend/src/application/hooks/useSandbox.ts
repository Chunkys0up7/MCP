import { useState, useCallback, useEffect } from 'react';
import { Node, Edge } from 'reactflow';
import { WorkflowNode } from '../../domain/models/workflow';
import { sandboxService, SandboxConfig, SandboxResult, ComponentTest } from '../../infrastructure/services/sandboxService';

export const useSandbox = (workflowId: string) => {
  const [sandboxId, setSandboxId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<{
    executionTime: number;
    memoryUsage: number;
    cpuUsage: number;
  } | null>(null);

  const createSandbox = useCallback(async (config: SandboxConfig) => {
    try {
      setIsLoading(true);
      setError(null);
      const id = await sandboxService.createSandbox(workflowId, config);
      setSandboxId(id);
      return id;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create sandbox');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [workflowId]);

  const executeInSandbox = useCallback(async (
    nodes: Node<WorkflowNode>[],
    edges: Edge[],
    input: any
  ): Promise<SandboxResult> => {
    if (!sandboxId) {
      throw new Error('No active sandbox');
    }

    try {
      setIsLoading(true);
      setError(null);
      const result = await sandboxService.executeInSandbox(sandboxId, nodes, edges, input);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute in sandbox');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sandboxId]);

  const runTests = useCallback(async (
    componentId: string,
    tests: ComponentTest[]
  ) => {
    if (!sandboxId) {
      throw new Error('No active sandbox');
    }

    try {
      setIsLoading(true);
      setError(null);
      const result = await sandboxService.runComponentTests(sandboxId, componentId, tests);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run tests');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sandboxId]);

  const validateInput = useCallback(async (
    componentId: string,
    input: any
  ) => {
    if (!sandboxId) {
      throw new Error('No active sandbox');
    }

    try {
      setIsLoading(true);
      setError(null);
      const result = await sandboxService.validateInput(sandboxId, componentId, input);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate input');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sandboxId]);

  const updateMetrics = useCallback(async () => {
    if (!sandboxId) return;

    try {
      const newMetrics = await sandboxService.collectMetrics(sandboxId);
      setMetrics(newMetrics);
    } catch (err) {
      console.error('Failed to update metrics:', err);
    }
  }, [sandboxId]);

  const cleanup = useCallback(async () => {
    if (!sandboxId) return;

    try {
      setIsLoading(true);
      setError(null);
      await sandboxService.cleanupSandbox(sandboxId);
      setSandboxId(null);
      setMetrics(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cleanup sandbox');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sandboxId]);

  // Update metrics periodically
  useEffect(() => {
    if (!sandboxId) return;

    const interval = setInterval(updateMetrics, 1000);
    return () => clearInterval(interval);
  }, [sandboxId, updateMetrics]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (sandboxId) {
        cleanup().catch(console.error);
      }
    };
  }, [sandboxId, cleanup]);

  return {
    sandboxId,
    isLoading,
    error,
    metrics,
    createSandbox,
    executeInSandbox,
    runTests,
    validateInput,
    updateMetrics,
    cleanup
  };
}; 