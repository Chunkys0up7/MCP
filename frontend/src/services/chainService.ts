import axios from 'axios';
import type { ChainService, Chain, ChainConfig } from '../types';

export class ChainServiceImpl implements ChainService {
  private baseUrl: string;
  private api = axios.create();

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.api.defaults.baseURL = baseUrl;
    this.api.defaults.headers.common['Content-Type'] = 'application/json';
  }

  async getChain(id: string): Promise<Chain> {
    try {
      const response = await this.api.get(`/chains/${id}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to get chain');
      }
      throw error;
    }
  }

  async updateChainConfig(id: string, config: Partial<ChainConfig>): Promise<Chain> {
    try {
      const response = await this.api.patch(`/chains/${id}/config`, config);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to update chain config');
      }
      throw error;
    }
  }

  async executeChain(id: string): Promise<void> {
    try {
      await this.api.post(`/chains/${id}/execute`);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to execute chain');
      }
      throw error;
    }
  }

  async stopExecution(id: string): Promise<void> {
    try {
      await this.api.post(`/chains/${id}/stop`);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to stop chain');
      }
      throw error;
    }
  }
} 