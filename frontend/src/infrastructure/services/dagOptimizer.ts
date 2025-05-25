import { Node, Edge } from 'reactflow';
import { WorkflowNode } from '../../domain/models/workflow';

interface CostEstimate {
  executionTime: number;
  memoryUsage: number;
  cpuUsage: number;
  networkCost: number;
}

interface OptimizationResult {
  isValid: boolean;
  cycles: string[][];
  parallelGroups: string[][];
  costEstimate: CostEstimate;
  suggestions: string[];
}

export class DAGOptimizer {
  private nodes: Node<WorkflowNode>[];
  private edges: Edge[];

  constructor(nodes: Node<WorkflowNode>[], edges: Edge[]) {
    this.nodes = nodes;
    this.edges = edges;
  }

  /**
   * Validates the DAG and returns optimization results
   */
  public optimize(): OptimizationResult {
    const cycles = this.detectCycles();
    const parallelGroups = this.findParallelGroups();
    const costEstimate = this.estimateCosts();
    const suggestions = this.generateOptimizationSuggestions(cycles, parallelGroups, costEstimate);

    return {
      isValid: cycles.length === 0,
      cycles,
      parallelGroups,
      costEstimate,
      suggestions
    };
  }

  /**
   * Detects cycles in the DAG using depth-first search
   */
  private detectCycles(): string[][] {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();
    const cycles: string[][] = [];

    const dfs = (nodeId: string, path: string[]) => {
      visited.add(nodeId);
      recursionStack.add(nodeId);
      path.push(nodeId);

      const outgoingEdges = this.edges.filter(edge => edge.source === nodeId);
      for (const edge of outgoingEdges) {
        const targetId = edge.target;
        if (!visited.has(targetId)) {
          dfs(targetId, [...path]);
        } else if (recursionStack.has(targetId)) {
          // Found a cycle
          const cycleStart = path.indexOf(targetId);
          cycles.push(path.slice(cycleStart));
        }
      }

      recursionStack.delete(nodeId);
    };

    for (const node of this.nodes) {
      if (!visited.has(node.id)) {
        dfs(node.id, []);
      }
    }

    return cycles;
  }

  /**
   * Finds groups of nodes that can be executed in parallel
   */
  private findParallelGroups(): string[][] {
    const groups: string[][] = [];
    const visited = new Set<string>();
    const inDegree = new Map<string, number>();

    // Calculate in-degree for each node
    for (const edge of this.edges) {
      inDegree.set(edge.target, (inDegree.get(edge.target) || 0) + 1);
    }

    // Find nodes with no dependencies (in-degree = 0)
    const findRootNodes = () => {
      return this.nodes
        .filter(node => !inDegree.has(node.id) || inDegree.get(node.id) === 0)
        .map(node => node.id);
    };

    // Process nodes level by level
    while (visited.size < this.nodes.length) {
      const currentLevel = findRootNodes();
      if (currentLevel.length > 0) {
        groups.push(currentLevel);
        currentLevel.forEach(nodeId => {
          visited.add(nodeId);
          // Update in-degree for child nodes
          this.edges
            .filter(edge => edge.source === nodeId)
            .forEach(edge => {
              inDegree.set(edge.target, (inDegree.get(edge.target) || 0) - 1);
            });
        });
      } else {
        // If no root nodes found but still have unvisited nodes, there must be a cycle
        break;
      }
    }

    return groups;
  }

  /**
   * Estimates execution costs for the workflow
   */
  private estimateCosts(): CostEstimate {
    const executionTime = this.estimateExecutionTime();
    const memoryUsage = this.estimateMemoryUsage();
    const cpuUsage = this.estimateCpuUsage();
    const networkCost = this.estimateNetworkCost();

    return {
      executionTime,
      memoryUsage,
      cpuUsage,
      networkCost
    };
  }

  private estimateExecutionTime(): number {
    // Simple estimation based on node types and connections
    let totalTime = 0;
    for (const node of this.nodes) {
      const nodeType = node.data.type;
      const baseTime = this.getBaseExecutionTime(nodeType);
      const connectionFactor = this.getConnectionFactor(node.id);
      totalTime += baseTime * connectionFactor;
    }
    return totalTime;
  }

  private estimateMemoryUsage(): number {
    // Estimate memory usage based on node types and data size
    let totalMemory = 0;
    for (const node of this.nodes) {
      const nodeType = node.data.type;
      const baseMemory = this.getBaseMemoryUsage(nodeType);
      const dataSize = this.estimateDataSize(node.id);
      totalMemory += baseMemory + dataSize;
    }
    return totalMemory;
  }

  private estimateCpuUsage(): number {
    // Estimate CPU usage based on node types and complexity
    let totalCpu = 0;
    for (const node of this.nodes) {
      const nodeType = node.data.type;
      const baseCpu = this.getBaseCpuUsage(nodeType);
      const complexityFactor = this.getComplexityFactor(node.id);
      totalCpu += baseCpu * complexityFactor;
    }
    return totalCpu;
  }

  private estimateNetworkCost(): number {
    // Estimate network cost based on data transfer between nodes
    let totalCost = 0;
    for (const edge of this.edges) {
      const sourceNode = this.nodes.find(n => n.id === edge.source);
      const targetNode = this.nodes.find(n => n.id === edge.target);
      if (sourceNode && targetNode) {
        const dataSize = this.estimateDataSize(sourceNode.id);
        const transferCost = this.getTransferCost(sourceNode.data.type, targetNode.data.type);
        totalCost += dataSize * transferCost;
      }
    }
    return totalCost;
  }

  private getBaseExecutionTime(nodeType: string): number {
    // Base execution time in milliseconds for different node types
    const baseTimes: Record<string, number> = {
      'data-source': 100,
      'transformation': 200,
      'aggregation': 300,
      'output': 50
    };
    return baseTimes[nodeType] || 100;
  }

  private getBaseMemoryUsage(nodeType: string): number {
    // Base memory usage in MB for different node types
    const baseMemory: Record<string, number> = {
      'data-source': 50,
      'transformation': 100,
      'aggregation': 150,
      'output': 25
    };
    return baseMemory[nodeType] || 50;
  }

  private getBaseCpuUsage(nodeType: string): number {
    // Base CPU usage in percentage for different node types
    const baseCpu: Record<string, number> = {
      'data-source': 20,
      'transformation': 40,
      'aggregation': 60,
      'output': 10
    };
    return baseCpu[nodeType] || 20;
  }

  private getConnectionFactor(nodeId: string): number {
    // Factor based on number of incoming and outgoing connections
    const incoming = this.edges.filter(e => e.target === nodeId).length;
    const outgoing = this.edges.filter(e => e.source === nodeId).length;
    return 1 + (incoming + outgoing) * 0.1;
  }

  private getComplexityFactor(nodeId: string): number {
    // Factor based on node complexity (can be enhanced with more sophisticated logic)
    const node = this.nodes.find(n => n.id === nodeId);
    if (!node) return 1;
    const config = (node.data as any).config;
    return 1 + (config?.complexity || 0) * 0.2;
  }

  private estimateDataSize(nodeId: string): number {
    // Estimate data size in MB (can be enhanced with actual data size estimation)
    const node = this.nodes.find(n => n.id === nodeId);
    if (!node) return 0;
    const config = (node.data as any).config;
    return (config?.estimatedDataSize || 10);
  }

  private getTransferCost(sourceType: string, targetType: string): number {
    // Cost factor for data transfer between different node types
    const transferCosts: Record<string, Record<string, number>> = {
      'data-source': {
        'transformation': 0.1,
        'aggregation': 0.2,
        'output': 0.05
      },
      'transformation': {
        'aggregation': 0.15,
        'output': 0.1
      },
      'aggregation': {
        'output': 0.05
      }
    };
    return transferCosts[sourceType]?.[targetType] || 0.1;
  }

  /**
   * Generates optimization suggestions based on analysis results
   */
  private generateOptimizationSuggestions(
    cycles: string[][],
    parallelGroups: string[][],
    costEstimate: CostEstimate
  ): string[] {
    const suggestions: string[] = [];

    // Add suggestions for cycles
    if (cycles.length > 0) {
      suggestions.push('Detected cycles in workflow. Consider restructuring to remove circular dependencies.');
      cycles.forEach((cycle, index) => {
        suggestions.push(`Cycle ${index + 1}: ${cycle.join(' -> ')}`);
      });
    }

    // Add suggestions for parallel execution
    if (parallelGroups.length > 0) {
      const maxParallelGroup = parallelGroups.reduce((max, group) => 
        group.length > max.length ? group : max, parallelGroups[0]);
      if (maxParallelGroup.length > 1) {
        suggestions.push(`Consider parallelizing execution of nodes: ${maxParallelGroup.join(', ')}`);
      }
    }

    // Add suggestions based on cost estimates
    if (costEstimate.executionTime > 1000) {
      suggestions.push('High execution time detected. Consider optimizing slow nodes or adding caching.');
    }
    if (costEstimate.memoryUsage > 500) {
      suggestions.push('High memory usage detected. Consider optimizing memory-intensive operations.');
    }
    if (costEstimate.cpuUsage > 80) {
      suggestions.push('High CPU usage detected. Consider distributing load or optimizing CPU-intensive operations.');
    }
    if (costEstimate.networkCost > 100) {
      suggestions.push('High network cost detected. Consider optimizing data transfer or adding local caching.');
    }

    return suggestions;
  }
} 