// DEPRECATED: Use workflowService.ts instead. This file will be removed.
import { ApiClient } from '../api/client';
import type { Chain, ChainConfig, ChainInfo } from '../types/chain';
import type { ChainNode, ChainEdge } from '../types/chain';

export interface ChainService {
  getChain(id: string): Promise<Chain>;
  updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<Chain>;
  executeChain(id: string): Promise<void>;
  stopExecution(id: string): Promise<void>;
  getExecutionStatus(chainId: string, executionId: string): Promise<{
    status: 'running' | 'completed' | 'failed';
    progress: number;
    results?: Record<string, unknown>;
    error?: string;
  }>;
}

export class ChainError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly details?: unknown
  ) {
    super(message);
    this.name = 'ChainError';
  }
}

export class ChainServiceImpl implements ChainService {
  private client: ApiClient;

  constructor(baseURL: string) {
    this.client = new ApiClient(baseURL, import.meta.env.VITE_API_KEY || '');
  }

  private handleError(error: unknown): never {
    if (error instanceof Error) {
      throw new ChainError(
        error.message,
        'CHAIN_ERROR',
        error
      );
    }
    throw new ChainError(
      'An unknown error occurred',
      'UNKNOWN_ERROR',
      error
    );
  }

  async getChain(id: string): Promise<Chain> {
    try {
      return await this.client.getChain(id);
    } catch (error) {
      this.handleError(error);
    }
  }

  async updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<Chain> {
    try {
      return await this.client.updateChainConfig(id, config);
    } catch (error) {
      this.handleError(error);
    }
  }

  async executeChain(id: string): Promise<void> {
    try {
      await this.client.executeChain(id);
    } catch (error) {
      this.handleError(error);
    }
  }

  async stopExecution(id: string): Promise<void> {
    try {
      await this.client.stopExecution(id);
    } catch (error) {
      this.handleError(error);
    }
  }

  async getExecutionStatus(chainId: string, executionId: string): Promise<{
    status: 'running' | 'completed' | 'failed';
    progress: number;
    results?: Record<string, unknown>;
    error?: string;
  }> {
    try {
      return await this.client.getExecutionStatus(chainId, executionId);
    } catch (error) {
      this.handleError(error);
    }
  }
} 