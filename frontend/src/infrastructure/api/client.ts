import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig } from 'axios';
import type { Node, Edge } from 'reactflow';
import { withRateLimit } from './rateLimiter';
import { captureException } from '../monitoring/sentry';

const API_BASE_URL = 'http://localhost:8000';

export interface ChainConfig {
  errorHandling: {
    strategy: 'retry' | 'fallback' | 'ignore';
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
  createdAt: string;
  updatedAt: string;
}

export interface ChainCreateInfo {
  name: string;
  description: string;
  config: ChainConfig;
}

export interface ChainUpdateInfo {
  name?: string;
  description?: string;
}

export interface ExecutionResult {
  nodeId: string;
  status: 'running' | 'completed' | 'error';
  result?: unknown;
  error?: string;
}

export class ApiClient {
  private client: AxiosInstance;
  private readonly API_KEY: string;

  constructor(baseURL: string, apiKey: string) {
    this.API_KEY = apiKey;
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.API_KEY,
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        captureException(error, {
          url: error.config?.url,
          method: error.config?.method,
          status: error.response?.status,
        });
        return Promise.reject(error);
      }
    );
  }

  private async request<T>(config: AxiosRequestConfig): Promise<T> {
    const endpoint = config.url || '';
    return withRateLimit(
      `${config.method}-${endpoint}`,
      async () => {
        const response = await this.client.request<T>(config);
        return response.data;
      },
      () => {
        captureException(new Error('Rate limit exceeded'), {
          endpoint,
          method: config.method,
        });
      }
    );
  }

  // Chain Management
  async getChains(): Promise<ChainInfo[]> {
    return this.request<ChainInfo[]>({
      method: 'GET',
      url: '/chains',
    });
  }

  async getChain(id: string): Promise<ChainInfo> {
    return this.request<ChainInfo>({
      method: 'GET',
      url: `/chains/${id}`,
    });
  }

  async createChain(info: ChainCreateInfo): Promise<ChainInfo> {
    return this.request<ChainInfo>({
      method: 'POST',
      url: '/chains',
      data: info,
    });
  }

  async updateChain(id: string, info: ChainUpdateInfo): Promise<ChainInfo> {
    return this.request<ChainInfo>({
      method: 'PATCH',
      url: `/chains/${id}`,
      data: info,
    });
  }

  async updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<ChainInfo> {
    return this.request<ChainInfo>({
      method: 'PATCH',
      url: `/chains/${id}/config`,
      data: { config },
    });
  }

  async deleteChain(id: string): Promise<void> {
    return this.request<void>({
      method: 'DELETE',
      url: `/chains/${id}`,
    });
  }

  // Chain Execution
  async executeChain(id: string): Promise<{ executionId: string }> {
    return this.request<{ executionId: string }>({
      method: 'POST',
      url: `/chains/${id}/execute`,
    });
  }

  async getExecutionStatus(
    chainId: string,
    executionId: string
  ): Promise<{
    status: 'running' | 'completed' | 'failed';
    progress: number;
    results?: Record<string, unknown>;
    error?: string;
  }> {
    return this.request<{
      status: 'running' | 'completed' | 'failed';
      progress: number;
      results?: Record<string, unknown>;
      error?: string;
    }>({
      method: 'GET',
      url: `/chains/${chainId}/executions/${executionId}`,
    });
  }

  async stopExecution(id: string): Promise<void> {
    await this.client.post(`/chains/${id}/stop`);
  }
}

export const apiClient = new ApiClient(API_BASE_URL, 'your-api-key'); 