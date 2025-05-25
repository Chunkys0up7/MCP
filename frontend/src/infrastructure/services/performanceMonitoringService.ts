import { Node, Edge } from 'reactflow';

export interface PerformanceMetric {
  id: string;
  type: 'node' | 'workflow' | 'network';
  name: string;
  value: number;
  unit: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface NodePerformance {
  nodeId: string;
  executionTime: number;
  memoryUsage: number;
  cpuUsage: number;
  networkRequests: number;
  cacheHits: number;
  cacheMisses: number;
}

export interface WorkflowPerformance {
  workflowId: string;
  totalExecutionTime: number;
  nodePerformance: Record<string, NodePerformance>;
  networkLatency: number;
  dataTransferSize: number;
  cacheEfficiency: number;
}

class PerformanceMonitoringService {
  private metrics: PerformanceMetric[] = [];
  private nodePerformance: Record<string, NodePerformance> = {};
  private workflowPerformance: Record<string, WorkflowPerformance> = {};
  private cacheStats: Record<string, { hits: number; misses: number }> = {};

  // Performance tracking methods
  trackNodeExecution(nodeId: string, executionTime: number, metadata?: Record<string, any>) {
    this.metrics.push({
      id: `node-${Date.now()}`,
      type: 'node',
      name: 'execution_time',
      value: executionTime,
      unit: 'ms',
      timestamp: new Date().toISOString(),
      metadata: { nodeId, ...metadata }
    });

    if (!this.nodePerformance[nodeId]) {
      this.nodePerformance[nodeId] = {
        nodeId,
        executionTime: 0,
        memoryUsage: 0,
        cpuUsage: 0,
        networkRequests: 0,
        cacheHits: 0,
        cacheMisses: 0
      };
    }

    this.nodePerformance[nodeId].executionTime += executionTime;
  }

  trackNetworkRequest(nodeId: string, latency: number, dataSize: number) {
    this.metrics.push({
      id: `network-${Date.now()}`,
      type: 'network',
      name: 'request_latency',
      value: latency,
      unit: 'ms',
      timestamp: new Date().toISOString(),
      metadata: { nodeId, dataSize }
    });

    if (this.nodePerformance[nodeId]) {
      this.nodePerformance[nodeId].networkRequests++;
    }
  }

  trackCacheOperation(nodeId: string, isHit: boolean) {
    if (!this.cacheStats[nodeId]) {
      this.cacheStats[nodeId] = { hits: 0, misses: 0 };
    }

    if (isHit) {
      this.cacheStats[nodeId].hits++;
      if (this.nodePerformance[nodeId]) {
        this.nodePerformance[nodeId].cacheHits++;
      }
    } else {
      this.cacheStats[nodeId].misses++;
      if (this.nodePerformance[nodeId]) {
        this.nodePerformance[nodeId].cacheMisses++;
      }
    }
  }

  // Performance analysis methods
  getNodePerformance(nodeId: string): NodePerformance | undefined {
    return this.nodePerformance[nodeId];
  }

  getWorkflowPerformance(workflowId: string): WorkflowPerformance | undefined {
    return this.workflowPerformance[workflowId];
  }

  getCacheEfficiency(nodeId: string): number {
    const stats = this.cacheStats[nodeId];
    if (!stats) return 0;
    const total = stats.hits + stats.misses;
    return total === 0 ? 0 : (stats.hits / total) * 100;
  }

  getMetricsByType(type: 'node' | 'workflow' | 'network'): PerformanceMetric[] {
    return this.metrics.filter(metric => metric.type === type);
  }

  getMetricsByTimeRange(startTime: string, endTime: string): PerformanceMetric[] {
    return this.metrics.filter(metric => 
      metric.timestamp >= startTime && metric.timestamp <= endTime
    );
  }

  // Performance optimization methods
  identifyBottlenecks(workflowId: string): string[] {
    const workflow = this.workflowPerformance[workflowId];
    if (!workflow) return [];

    const bottlenecks: string[] = [];
    const avgExecutionTime = workflow.totalExecutionTime / Object.keys(workflow.nodePerformance).length;

    Object.entries(workflow.nodePerformance).forEach(([nodeId, performance]) => {
      if (performance.executionTime > avgExecutionTime * 1.5) {
        bottlenecks.push(nodeId);
      }
    });

    return bottlenecks;
  }

  getOptimizationSuggestions(workflowId: string): string[] {
    const suggestions: string[] = [];
    const workflow = this.workflowPerformance[workflowId];
    if (!workflow) return suggestions;

    // Check cache efficiency
    Object.entries(this.cacheStats).forEach(([nodeId, stats]) => {
      const efficiency = this.getCacheEfficiency(nodeId);
      if (efficiency < 50) {
        suggestions.push(`Consider increasing cache size for node ${nodeId}`);
      }
    });

    // Check network performance
    Object.entries(workflow.nodePerformance).forEach(([nodeId, performance]) => {
      if (performance.networkRequests > 10) {
        suggestions.push(`Consider implementing request batching for node ${nodeId}`);
      }
    });

    return suggestions;
  }

  // Reset methods
  clearMetrics(): void {
    this.metrics = [];
  }

  clearNodePerformance(): void {
    this.nodePerformance = {};
  }

  clearWorkflowPerformance(): void {
    this.workflowPerformance = {};
  }

  clearCacheStats(): void {
    this.cacheStats = {};
  }
}

export const performanceMonitoringService = new PerformanceMonitoringService(); 