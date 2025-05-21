import client from '../api/client';
import type { IChainApi, ChainInfo, ChainConfig } from '../api/chainApi';

export interface ChainRepository {
  getChain(id: string): Promise<ChainInfo>;
  createChain(info: { name: string; description: string; config: ChainConfig }): Promise<ChainInfo>;
  updateChain(id: string, info: { name?: string; description?: string }): Promise<ChainInfo>;
  updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<ChainInfo>;
  deleteChain(id: string): Promise<void>;
  executeChain(id: string): Promise<{ executionId: string }>;
  getExecutionStatus(chainId: string, executionId: string): Promise<{
    status: 'running' | 'completed' | 'failed';
    progress: number;
    results?: Record<string, unknown>;
    error?: string;
  }>;
}

export class ChainRepositoryImpl implements ChainRepository {
  constructor(private readonly api: IChainApi) {}

  async getChain(id: string): Promise<ChainInfo> {
    const response = await client.get(`/chains/${id}`);
    return response.data;
  }

  async createChain(info: { name: string; description: string; config: ChainConfig }): Promise<ChainInfo> {
    const response = await client.post('/chains', info);
    return response.data;
  }

  async updateChain(id: string, info: { name?: string; description?: string }): Promise<ChainInfo> {
    const response = await client.put(`/chains/${id}`, info);
    return response.data;
  }

  async updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<ChainInfo> {
    const response = await client.put(`/chains/${id}/config`, config);
    return response.data;
  }

  async deleteChain(id: string): Promise<void> {
    await client.delete(`/chains/${id}`);
  }

  async executeChain(id: string): Promise<{ executionId: string }> {
    const response = await client.post(`/chains/${id}/execute`);
    return response.data;
  }

  async getExecutionStatus(chainId: string, executionId: string): Promise<{
    status: 'running' | 'completed' | 'failed';
    progress: number;
    results?: Record<string, unknown>;
    error?: string;
  }> {
    const response = await client.get(`/chains/${chainId}/executions/${executionId}`);
    return response.data;
  }
} 