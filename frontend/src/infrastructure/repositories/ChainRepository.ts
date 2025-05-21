import type { IChainApi, ChainInfo, ChainConfig } from '../api/chainApi';
import type { Node, Edge } from 'reactflow';
import type { NodeData } from '../types/node';

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
    try {
      return await this.api.getChain(id);
    } catch (error) {
      throw new Error(`Failed to get chain: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async createChain(info: { name: string; description: string; config: ChainConfig }): Promise<ChainInfo> {
    try {
      return await this.api.createChain(info);
    } catch (error) {
      throw new Error(`Failed to create chain: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async updateChain(id: string, info: { name?: string; description?: string }): Promise<ChainInfo> {
    try {
      return await this.api.updateChain(id, info);
    } catch (error) {
      throw new Error(`Failed to update chain: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<ChainInfo> {
    try {
      return await this.api.updateChainConfig(id, config);
    } catch (error) {
      throw new Error(`Failed to update chain config: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async deleteChain(id: string): Promise<void> {
    try {
      await this.api.deleteChain(id);
    } catch (error) {
      throw new Error(`Failed to delete chain: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async executeChain(id: string): Promise<{ executionId: string }> {
    try {
      return await this.api.executeChain(id);
    } catch (error) {
      throw new Error(`Failed to execute chain: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getExecutionStatus(chainId: string, executionId: string): Promise<{
    status: 'running' | 'completed' | 'failed';
    progress: number;
    results?: Record<string, unknown>;
    error?: string;
  }> {
    try {
      return await this.api.getExecutionStatus(chainId, executionId);
    } catch (error) {
      throw new Error(`Failed to get execution status: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
} 