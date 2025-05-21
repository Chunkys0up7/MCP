import type { Node, Edge } from 'reactflow';

// MCP Types
export interface MCPConfig {
  id: string;
  name: string;
  type: 'llm' | 'notebook' | 'data';
  description: string;
  version: string;
  author: string;
  tags: string[];
  config: Record<string, unknown>;
}

export interface MCPItem extends MCPConfig {
  status: 'idle' | 'running' | 'success' | 'error';
}

// Chain Types
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

export interface ChainNodeData {
  label: string;
  type: 'llm' | 'notebook' | 'data';
  config: Record<string, unknown>;
  status: 'idle' | 'running' | 'success' | 'error';
}

export interface ChainNode extends Omit<Node, 'type' | 'data'> {
  type: 'mcp';
  data: ChainNodeData;
}

export interface ChainEdge extends Omit<Edge, 'type'> {
  type?: string;
  animated?: boolean;
}

export interface Chain {
  info: ChainInfo;
  config: ChainConfig;
  nodes: ChainNode[];
  edges: ChainEdge[];
}

// Service Types
export interface ChainService {
  getChain(id: string): Promise<Chain>;
  updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<Chain>;
  executeChain(id: string): Promise<void>;
  stopExecution(id: string): Promise<void>;
}

// Store Types
export interface ChainState {
  chainInfo: ChainInfo | null;
  chainConfig: ChainConfig | null;
  nodes: ChainNode[];
  edges: ChainEdge[];
  isLoading: boolean;
  error: string | null;
  isExecuting: boolean;
  selectedNode: Node | null;
  chainService: ChainService | null;
} 