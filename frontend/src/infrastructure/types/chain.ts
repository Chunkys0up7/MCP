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

export interface ChainConfig {
  errorHandling: {
    strategy: 'retry' | 'skip' | 'fail';
    maxRetries: number;
    backoffFactor: number;
  };
  executionMode: 'sequential' | 'parallel';
  nodes?: ChainNode[];
  edges?: ChainEdge[];
}

export interface ChainInfo {
  id: string;
  name: string;
  description: string;
  config: ChainConfig;
  nodes: ChainNode[];
  edges: ChainEdge[];
  createdAt: string;
  updatedAt: string;
} 