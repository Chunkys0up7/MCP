import type { MCPConfig } from './mcp';

export type NodeStatus = 'idle' | 'running' | 'success' | 'error';

export interface NodeData {
  label: string;
  type: string;
  status: NodeStatus;
  config?: MCPConfig;
  inputValues?: Record<string, string>;
}

export interface MCPItem {
  id: string;
  name: string;
  type: 'llm' | 'notebook' | 'data';
  description: string;
} 