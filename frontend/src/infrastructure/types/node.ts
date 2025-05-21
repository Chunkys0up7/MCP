import type { MCPConfig } from './mcp';

export type NodeStatus = 'idle' | 'running' | 'success' | 'error';
export type NodeType = 'llm' | 'notebook' | 'data';

export interface NodeData {
  label: string;
  type: NodeType;
  status: NodeStatus;
  config?: MCPConfig;
  inputValues?: Record<string, string>;
  description?: string;
  onDelete?: (nodeId: string) => void;
  onConfigure?: (nodeId: string) => void;
}

export interface MCPItem {
  id: string;
  name: string;
  type: NodeType;
  description: string;
  config?: Record<string, unknown>;
}

export interface NodeConfig {
  llm: {
    model: string;
    temperature: number;
    maxTokens: number;
    prompt: string;
  };
  notebook: {
    name: string;
    description: string;
    tags: string[];
  };
  data: {
    source: string;
    format: string;
    schema: string;
  };
}

export interface NodeConfigData {
  label: string;
  type: NodeType;
  config: NodeConfig[NodeType];
} 