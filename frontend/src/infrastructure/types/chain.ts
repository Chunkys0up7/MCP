import type { Node, Edge } from 'reactflow';
import type { NodeType } from './node';

export interface ChainNodeData {
  label: string;
  config: Record<string, unknown>;
  status: 'idle' | 'running' | 'success' | 'error';
  description?: string;
  inputValues?: Record<string, string>;
}

export interface ChainNode extends Omit<Node, 'type' | 'data'> {
  type: NodeType;
  data: ChainNodeData;
}

export interface ChainEdge extends Omit<Edge, 'type'> {
  type: 'smoothstep' | 'straight' | 'step' | 'default';
  animated: boolean;
  label?: string;
}

export interface ChainInfo {
  id: string;
  name: string;
  description: string;
  version: string;
  createdAt: string;
  updatedAt: string;
  author: string;
  tags: string[];
}

export interface ChainConfig {
  errorHandling: {
    retryCount: number;
    retryDelay: number;
    failFast: boolean;
  };
  executionMode: 'sequential' | 'parallel';
  timeout: number;
  maxConcurrent: number;
  validation: {
    validateInputs: boolean;
    validateOutputs: boolean;
    strictMode: boolean;
  };
}

export interface Chain {
  info: ChainInfo;
  config: ChainConfig;
  nodes: ChainNode[];
  edges: ChainEdge[];
  metadata: {
    lastExecuted?: string;
    executionCount: number;
    averageExecutionTime: number;
    successRate: number;
  };
} 