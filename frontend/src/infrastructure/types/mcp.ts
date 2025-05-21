export type MCPType = 'llm' | 'notebook' | 'data';

export interface MCPConfig {
  model?: string;
  temperature?: number;
  maxTokens?: number;
  notebookPath?: string;
  dataSource?: string;
  [key: string]: any;
}

export interface MCPItem {
  id: string;
  name: string;
  type: MCPType;
  description?: string;
  config?: MCPConfig;
  version?: string;
  author?: string;
  tags?: string[];
} 