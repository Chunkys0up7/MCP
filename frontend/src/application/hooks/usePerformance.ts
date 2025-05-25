import { useState, useCallback, useEffect } from 'react';
import { Node, Edge } from 'reactflow';
import { performanceMonitoringService, PerformanceMetric, NodePerformance, WorkflowPerformance } from '../../infrastructure/services/performanceMonitoringService';
import { cacheService } from '../../infrastructure/services/cacheService';

export const usePerformance = (workflowId: string, nodes: Node[], edges: Edge[]) => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [nodePerformance, setNodePerformance] = useState<Record<string, NodePerformance>>({});
  const [workflowPerformance, setWorkflowPerformance] = useState<WorkflowPerformance | null>(null);
  const [cacheStats, setCacheStats] = useState<{ hits: number; misses: number }>({ hits: 0, misses: 0 });

  // Performance tracking
  const trackNodeExecution = useCallback((nodeId: string, executionTime: number, metadata?: Record<string, any>) => {
    performanceMonitoringService.trackNodeExecution(nodeId, executionTime, metadata);
    setNodePerformance(prev => ({
      ...prev,
      [nodeId]: performanceMonitoringService.getNodePerformance(nodeId) || prev[nodeId]
    }));
  }, []);

  const trackNetworkRequest = useCallback((nodeId: string, latency: number, dataSize: number) => {
    performanceMonitoringService.trackNetworkRequest(nodeId, latency, dataSize);
    setNodePerformance(prev => ({
      ...prev,
      [nodeId]: performanceMonitoringService.getNodePerformance(nodeId) || prev[nodeId]
    }));
  }, []);

  // Cache management
  const getCachedResult = useCallback(async <T>(key: string): Promise<T | null> => {
    const result = await cacheService.get<T>(key);
    setCacheStats(prev => ({
      hits: result ? prev.hits + 1 : prev.hits,
      misses: !result ? prev.misses + 1 : prev.misses
    }));
    return result;
  }, []);

  const setCachedResult = useCallback(async <T>(key: string, value: T, options?: { ttl?: number; metadata?: Record<string, any> }) => {
    await cacheService.set(key, value, options);
  }, []);

  // Performance analysis
  const getBottlenecks = useCallback(() => {
    return performanceMonitoringService.identifyBottlenecks(workflowId);
  }, [workflowId]);

  const getOptimizationSuggestions = useCallback(() => {
    return performanceMonitoringService.getOptimizationSuggestions(workflowId);
  }, [workflowId]);

  // Metrics collection
  useEffect(() => {
    const interval = setInterval(() => {
      const newMetrics = performanceMonitoringService.getMetricsByType('node');
      setMetrics(newMetrics);
      setWorkflowPerformance(performanceMonitoringService.getWorkflowPerformance(workflowId) || null);
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [workflowId]);

  return {
    // Performance tracking
    trackNodeExecution,
    trackNetworkRequest,
    
    // Cache management
    getCachedResult,
    setCachedResult,
    
    // Performance analysis
    getBottlenecks,
    getOptimizationSuggestions,
    
    // State
    metrics,
    nodePerformance,
    workflowPerformance,
    cacheStats
  };
}; 