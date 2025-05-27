import axios from 'axios';
import type { Node, Edge } from 'reactflow';
import type { NodeData } from '../types/node';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3000/api';

export interface ChainConfig {
  errorHandling: {
    strategy: 'retry' | 'skip' | 'fail';
    maxRetries: number;
    backoffFactor: number;
  };
  executionMode: 'sequential' | 'parallel';
}

export interface ChainInfo {
  id: string;
  name: string;
  description: string;
  config: ChainConfig;
  nodes: Node<NodeData>[];
  edges: Edge[];
  createdAt: string;
  updatedAt: string;
}

export interface CreateChainRequest {
  name: string;
  description: string;
  config: ChainConfig;
}

export interface UpdateChainRequest {
  name?: string;
  description?: string;
  config?: Partial<ChainConfig>;
}

export interface IChainApi {
  getChain: (id: string) => Promise<ChainInfo>;
  createChain: (info: { name: string; description: string; config: ChainConfig }) => Promise<ChainInfo>;
  updateChain: (id: string, info: { name?: string; description?: string }) => Promise<ChainInfo>;
  updateChainConfig: (id: string, config: Partial<ChainConfig>) => Promise<ChainInfo>;
  deleteChain: (id: string) => Promise<void>;
  executeChain: (id: string) => Promise<{ executionId: string }>;
  getExecutionStatus: (chainId: string, executionId: string) => Promise<{
    status: 'running' | 'completed' | 'failed';
    progress: number;
    results?: Record<string, unknown>;
    error?: string;
  }>;
}

class ChainApi implements IChainApi {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Chain CRUD operations
  async createChain(data: CreateChainRequest): Promise<ChainInfo> {
    const response = await this.api.post<ChainInfo>('/chains', data);
    return response.data;
  }

  async getChain(id: string): Promise<ChainInfo> {
    const response = await this.api.get<ChainInfo>(`/chains/${id}`);
    return response.data;
  }

  async updateChain(id: string, data: UpdateChainRequest): Promise<ChainInfo> {
    const response = await this.api.patch<ChainInfo>(`/chains/${id}`, data);
    return response.data;
  }

  async deleteChain(id: string): Promise<void> {
    await this.api.delete(`/chains/${id}`);
  }

  // Chain configuration operations
  async updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<ChainInfo> {
    const response = await this.api.patch<ChainInfo>(`/chains/${id}/config`, { config });
    return response.data;
  }

  // Chain execution operations
  async executeChain(id: string): Promise<{ executionId: string }> {
    const response = await this.api.post<{ executionId: string }>(`/chains/${id}/execute`);
    return response.data;
  }

  async getExecutionStatus(chainId: string, executionId: string): Promise<{
    status: 'running' | 'completed' | 'failed';
    progress: number;
    results?: Record<string, unknown>;
    error?: string;
  }> {
    const response = await this.api.get(`/chains/${chainId}/executions/${executionId}`);
    return response.data;
  }

  // Error handling
  private handleError(error: unknown): never {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        throw new Error(error.response.data.message || 'An error occurred');
      } else if (error.request) {
        throw new Error('No response received from server');
      }
    }
    throw new Error('An unexpected error occurred');
  }
}

export const chainApi = new ChainApi(); 