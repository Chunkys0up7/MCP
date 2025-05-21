import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { withRateLimit } from './rateLimiter';
import { captureException } from '../monitoring/sentry';
import type { Chain, ChainConfig, ChainInfo } from '../types/chain';

export interface ChainCreateInfo {
  name: string;
  description: string;
  config: ChainConfig;
  author: string;
  tags: string[];
}

export interface ChainUpdateInfo {
  name?: string;
  description?: string;
  config?: Partial<ChainConfig>;
  tags?: string[];
}

export interface ExecutionResult {
  nodeId: string;
  status: 'running' | 'completed' | 'error';
  result?: unknown;
  error?: string;
  startTime: string;
  endTime?: string;
  duration?: number;
}

export interface ExecutionStatus {
  status: 'running' | 'completed' | 'failed';
  progress: number;
  results?: Record<string, unknown>;
  error?: string;
  startTime: string;
  endTime?: string;
  duration?: number;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status: number,
    public readonly details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
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

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<{ message: string; code: string; details?: unknown }>) => {
        captureException(error, {
          url: error.config?.url,
          method: error.config?.method,
          status: error.response?.status,
        });

        if (error.response) {
          throw new ApiError(
            error.response.data?.message || 'An error occurred',
            error.response.data?.code || 'UNKNOWN_ERROR',
            error.response.status,
            error.response.data?.details
          );
        }

        throw new ApiError(
          'Network error occurred',
          'NETWORK_ERROR',
          0
        );
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
        throw new ApiError(
          'Rate limit exceeded',
          'RATE_LIMIT_EXCEEDED',
          429
        );
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

  async getChain(id: string): Promise<Chain> {
    return this.request<Chain>({
      method: 'GET',
      url: `/chains/${id}`,
    });
  }

  async createChain(info: ChainCreateInfo): Promise<Chain> {
    return this.request<Chain>({
      method: 'POST',
      url: '/chains',
      data: info,
    });
  }

  async updateChain(id: string, info: ChainUpdateInfo): Promise<Chain> {
    return this.request<Chain>({
      method: 'PATCH',
      url: `/chains/${id}`,
      data: info,
    });
  }

  async updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<Chain> {
    return this.request<Chain>({
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
  ): Promise<ExecutionStatus> {
    return this.request<ExecutionStatus>({
      method: 'GET',
      url: `/chains/${chainId}/executions/${executionId}`,
    });
  }

  async stopExecution(id: string): Promise<void> {
    return this.request<void>({
      method: 'POST',
      url: `/chains/${id}/stop`,
    });
  }
}

const client = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:3001',
  headers: {
    'Content-Type': 'application/json'
  }
});

export default client; 