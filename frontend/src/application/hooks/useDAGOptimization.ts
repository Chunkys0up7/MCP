import { useCallback, useEffect, useState } from 'react';
import { Node, Edge } from 'reactflow';
import { WorkflowNode } from '../../domain/models/workflow';
import { DAGOptimizer } from '../../infrastructure/services/dagOptimizer';

interface OptimizationState {
  isValid: boolean;
  cycles: string[][];
  parallelGroups: string[][];
  costEstimate: {
    executionTime: number;
    memoryUsage: number;
    cpuUsage: number;
    networkCost: number;
  };
  suggestions: string[];
}

export const useDAGOptimization = (nodes: Node<WorkflowNode>[], edges: Edge[]) => {
  const [optimizationState, setOptimizationState] = useState<OptimizationState>({
    isValid: true,
    cycles: [],
    parallelGroups: [],
    costEstimate: {
      executionTime: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      networkCost: 0
    },
    suggestions: []
  });

  const optimize = useCallback(() => {
    const optimizer = new DAGOptimizer(nodes, edges);
    const result = optimizer.optimize();
    setOptimizationState(result);
  }, [nodes, edges]);

  useEffect(() => {
    optimize();
  }, [optimize]);

  return {
    ...optimizationState,
    optimize
  };
}; 