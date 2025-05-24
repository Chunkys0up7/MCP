import { Node, Edge } from 'reactflow';
import { LLMService } from './llmService';
import { NotebookService } from './notebookService';
import { DataService } from './dataService';
import { apiClient } from './apiClient';
import { WorkflowExecutionResult } from '../../domain/models/workflow';

export interface ExecutionResult {
  nodeId: string;
  status: 'success' | 'error' | 'running' | 'pending';
  output?: any;
  error?: string;
  timestamp: number;
}

export interface ExecutionState {
  results: Record<string, ExecutionResult>;
  isRunning: boolean;
  currentNode?: string;
}

class WorkflowExecutionService {
  private state: ExecutionState = {
    results: {},
    isRunning: false,
  };

  private listeners: ((state: ExecutionState) => void)[] = [];

  constructor(
    private llmService: LLMService,
    private notebookService: NotebookService,
    private dataService: DataService
  ) {}

  subscribe(listener: (state: ExecutionState) => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener(this.state));
  }

  private updateState(update: Partial<ExecutionState>) {
    this.state = { ...this.state, ...update };
    this.notifyListeners();
  }

  private async executeNode(node: Node, input?: any): Promise<ExecutionResult> {
    const result: ExecutionResult = {
      nodeId: node.id,
      status: 'running',
      timestamp: Date.now(),
    };

    this.updateState({
      currentNode: node.id,
      results: { ...this.state.results, [node.id]: result },
    });

    try {
      let output: any;

      switch (node.data.type) {
        case 'llm':
          output = await this.llmService.execute({
            model: node.data.model,
            temperature: node.data.temperature,
            maxTokens: node.data.maxTokens,
            input,
          });
          break;

        case 'notebook':
          output = await this.notebookService.execute({
            path: node.data.notebookPath,
            kernel: node.data.kernel,
            timeout: node.data.timeout,
            input,
          });
          break;

        case 'data':
          output = await this.dataService.execute({
            type: node.data.dataType,
            source: node.data.source,
            format: node.data.format,
          });
          break;

        default:
          throw new Error(`Unknown node type: ${node.data.type}`);
      }

      result.status = 'success';
      result.output = output;
    } catch (error) {
      result.status = 'error';
      result.error = error instanceof Error ? error.message : 'Unknown error occurred';
    }

    this.updateState({
      results: { ...this.state.results, [node.id]: result },
    });

    return result;
  }

  private getNextNode(nodes: Node[], edges: Edge[], currentNode?: string): Node | undefined {
    if (!currentNode) {
      // Find nodes with no incoming edges
      const startNodes = nodes.filter(node => 
        !edges.some(edge => edge.target === node.id)
      );
      return startNodes[0];
    }

    // Find the next node in the workflow
    const nextEdge = edges.find(edge => edge.source === currentNode);
    if (!nextEdge) return undefined;

    return nodes.find(node => node.id === nextEdge.target);
  }

  async executeWorkflow(nodes: Node[], edges: Edge[]) {
    if (this.state.isRunning) {
      throw new Error('Workflow is already running');
    }

    this.updateState({
      isRunning: true,
      results: {},
      currentNode: undefined,
    });

    try {
      let currentNode = this.getNextNode(nodes, edges);
      let lastOutput: any;

      while (currentNode) {
        const result = await this.executeNode(currentNode, lastOutput);
        
        if (result.status === 'error') {
          throw new Error(`Node ${currentNode.id} failed: ${result.error}`);
        }

        lastOutput = result.output;
        currentNode = this.getNextNode(nodes, edges, currentNode.id);
      }
    } finally {
      this.updateState({ isRunning: false });
    }
  }

  stopExecution() {
    if (!this.state.isRunning) return;
    
    this.updateState({
      isRunning: false,
      currentNode: undefined,
    });
  }

  getExecutionState(): ExecutionState {
    return { ...this.state };
  }

  private baseUrl = '/api/workflows';

  async startExecution(workflowId: string): Promise<void> {
    await apiClient.post(`${this.baseUrl}/${workflowId}/execute`);
  }

  async stopExecution(workflowId: string): Promise<void> {
    await apiClient.post(`${this.baseUrl}/${workflowId}/stop`);
  }

  async getExecutionStatus(workflowId: string): Promise<WorkflowExecutionResult> {
    const response = await apiClient.get(`${this.baseUrl}/${workflowId}/status`);
    return response.data;
  }

  async getExecutionHistory(workflowId: string): Promise<WorkflowExecutionResult[]> {
    const response = await apiClient.get(`${this.baseUrl}/${workflowId}/history`);
    return response.data;
  }
}

export const workflowExecutionService = new WorkflowExecutionService(
  new LLMService(),
  new NotebookService(),
  new DataService()
); 