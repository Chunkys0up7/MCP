export type MCPType = 'llm' | 'notebook' | 'data';

export interface LLMConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  prompt: string;
}

export interface NotebookConfig {
  notebookPath: string;
  description: string;
  tags: string[];
}

export interface DataConfig {
  dataSource: string;
  format: string;
  schema: string;
}

export type MCPConfig = {
  llm: LLMConfig;
  notebook: NotebookConfig;
  data: DataConfig;
}[MCPType];

export interface MCPItem {
  id: string;
  name: string;
  type: MCPType;
  description: string;
  config?: MCPConfig;
  version: string;
  author: string;
  tags: string[];
} 