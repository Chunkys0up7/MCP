import { Node, Edge } from 'reactflow';
import { WorkflowNode } from '../../domain/models/workflow';
import { apiClient } from './apiClient';

export interface SandboxConfig {
  timeout: number;
  maxMemory: number;
  maxCpu: number;
  environment: 'development' | 'testing' | 'production';
}

export interface SandboxResult {
  success: boolean;
  output: any;
  error?: string;
  metrics: {
    executionTime: number;
    memoryUsage: number;
    cpuUsage: number;
  };
}

export interface ComponentTest {
  id: string;
  name: string;
  input: any;
  expectedOutput: any;
  timeout?: number;
}

class SandboxService {
  private static instance: SandboxService;
  private activeSandboxes: Map<string, SandboxConfig> = new Map();

  private constructor() {}

  static getInstance(): SandboxService {
    if (!SandboxService.instance) {
      SandboxService.instance = new SandboxService();
    }
    return SandboxService.instance;
  }

  async createSandbox(workflowId: string, config: SandboxConfig): Promise<string> {
    try {
      const response = await apiClient.post('/api/sandbox/create', {
        workflowId,
        config
      });
      const sandboxId = response.data.sandboxId;
      this.activeSandboxes.set(sandboxId, config);
      return sandboxId;
    } catch (error) {
      console.error('Failed to create sandbox:', error);
      throw new Error('Failed to create sandbox environment');
    }
  }

  async executeInSandbox(
    sandboxId: string,
    nodes: Node<WorkflowNode>[],
    edges: Edge[],
    input: any
  ): Promise<SandboxResult> {
    try {
      const response = await apiClient.post(`/api/sandbox/${sandboxId}/execute`, {
        nodes,
        edges,
        input
      });
      return response.data;
    } catch (error) {
      console.error('Failed to execute in sandbox:', error);
      throw new Error('Failed to execute workflow in sandbox');
    }
  }

  async runComponentTests(
    sandboxId: string,
    componentId: string,
    tests: ComponentTest[]
  ): Promise<{ success: boolean; results: any[] }> {
    try {
      const response = await apiClient.post(`/api/sandbox/${sandboxId}/test`, {
        componentId,
        tests
      });
      return response.data;
    } catch (error) {
      console.error('Failed to run component tests:', error);
      throw new Error('Failed to run component tests');
    }
  }

  async validateInput(
    sandboxId: string,
    componentId: string,
    input: any
  ): Promise<{ isValid: boolean; errors: string[] }> {
    try {
      const response = await apiClient.post(`/api/sandbox/${sandboxId}/validate`, {
        componentId,
        input
      });
      return response.data;
    } catch (error) {
      console.error('Failed to validate input:', error);
      throw new Error('Failed to validate input');
    }
  }

  async collectMetrics(sandboxId: string): Promise<{
    executionTime: number;
    memoryUsage: number;
    cpuUsage: number;
  }> {
    try {
      const response = await apiClient.get(`/api/sandbox/${sandboxId}/metrics`);
      return response.data;
    } catch (error) {
      console.error('Failed to collect metrics:', error);
      throw new Error('Failed to collect sandbox metrics');
    }
  }

  async cleanupSandbox(sandboxId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/sandbox/${sandboxId}`);
      this.activeSandboxes.delete(sandboxId);
    } catch (error) {
      console.error('Failed to cleanup sandbox:', error);
      throw new Error('Failed to cleanup sandbox environment');
    }
  }

  getActiveSandboxes(): Map<string, SandboxConfig> {
    return this.activeSandboxes;
  }
}

export const sandboxService = SandboxService.getInstance(); 