import type { Node, Edge } from 'reactflow';

export interface ChainNodeData {
  label: string;
  config: Record<string, unknown>;
  status?: 'idle' | 'running' | 'success' | 'error';
}

export interface ChainNode extends Omit<Node, 'type' | 'data'> {
  type: 'llm' | 'notebook' | 'data';
  data: ChainNodeData;
}

export interface ChainEdge extends Omit<Edge, 'type'> {
  type?: string;
  animated?: boolean;
}

export interface ChainInfo {
  id: string;
  name: string;
  description: string;
  version: string;
  createdAt: string;
  updatedAt: string;
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
}

export interface Chain {
  info: ChainInfo;
  config: ChainConfig;
  nodes: any[];
  edges: any[];
} 