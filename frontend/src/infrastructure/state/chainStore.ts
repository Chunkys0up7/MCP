import { create } from 'zustand';
import { ChainService } from '../services/chainService';
import { ChainInfo, ChainConfig, ChainNode, ChainEdge, Chain } from '../types/chain';
import { handleError } from '../utils/errorHandling';
import type { Node } from 'reactflow';
import { captureException } from '../monitoring/error';

interface ChainState {
  // Chain data
  chainInfo: ChainInfo | null;
  chainConfig: ChainConfig | null;
  nodes: ChainNode[];
  edges: ChainEdge[];
  isLoading: boolean;
  error: string | null;
  isExecuting: boolean;
  selectedNode: Node | null;

  // Actions
  loadChain: (id: string) => Promise<void>;
  saveChain: () => Promise<void>;
  executeChain: () => Promise<void>;
  stopExecution: () => Promise<void>;
  updateNode: (nodeId: string, data: Partial<ChainNode>) => void;
  updateEdge: (edgeId: string, data: Partial<ChainEdge>) => void;
  addNode: (node: ChainNode) => void;
  addEdge: (edge: ChainEdge) => void;
  removeNode: (nodeId: string) => void;
  removeEdge: (edgeId: string) => void;
  clearError: () => void;
  setSelectedNode: (node: Node | null) => void;
  createEdge: (edge: ChainEdge) => void;

  // Services
  chainService: ChainService | null;
}

// Initial state
const initialState = {
  chainInfo: {
    id: '',
    name: 'New Chain',
    description: '',
    version: '1.0.0',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  chainConfig: {
    errorHandling: {
      retryCount: 3,
      retryDelay: 1000,
      failFast: false,
    },
    executionMode: 'sequential' as const,
    timeout: 30000,
    maxConcurrent: 1,
  },
  nodes: [],
  edges: [],
  isLoading: false,
  error: null,
  isExecuting: false,
  chainService: null,
  selectedNode: null,
};

export const useChainStore = create<ChainState>((set, get) => ({
  ...initialState,

  loadChain: async (id: string) => {
    const { chainService } = get();
    if (!chainService) {
      set({ error: 'Chain service not initialized' });
      return;
    }

    set({ isLoading: true, error: null });
    try {
      const chain = await chainService.getChain(id);
      set({ 
        chainInfo: chain.info,
        chainConfig: chain.config,
        nodes: chain.nodes,
        edges: chain.edges,
        isLoading: false 
      });
    } catch (error) {
      const { message } = handleError(error, { chainId: id, action: 'loadChain' });
      set({ error: message, isLoading: false });
      captureException(error);
    }
  },

  saveChain: async () => {
    const { chainInfo, chainConfig, nodes, edges, chainService } = get();
    if (!chainService || !chainInfo || !chainConfig) {
      set({ error: 'Chain service not initialized or no chain loaded' });
      return;
    }

    set({ isLoading: true, error: null });
    try {
      const updatedChain = await chainService.updateChainConfig(chainInfo.id, {
        errorHandling: chainConfig.errorHandling,
        executionMode: chainConfig.executionMode,
        timeout: chainConfig.timeout,
        maxConcurrent: chainConfig.maxConcurrent
      });
      set({ 
        chainInfo: updatedChain.info,
        chainConfig: updatedChain.config,
        isLoading: false 
      });
    } catch (error) {
      const { message } = handleError(error, { 
        chainId: chainInfo.id, 
        action: 'saveChain',
        nodeCount: nodes.length,
        edgeCount: edges.length
      });
      set({ error: message, isLoading: false });
      captureException(error);
    }
  },

  executeChain: async () => {
    const { chainInfo, chainService } = get();
    if (!chainService || !chainInfo) {
      set({ error: 'Chain service not initialized or no chain loaded' });
      return;
    }

    set({ isExecuting: true, error: null });
    try {
      await chainService.executeChain(chainInfo.id);
    } catch (error) {
      const { message } = handleError(error, { chainId: chainInfo.id, action: 'executeChain' });
      set({ error: message, isExecuting: false });
      captureException(error);
    }
  },

  stopExecution: async () => {
    const { chainInfo, chainService } = get();
    if (!chainService || !chainInfo) {
      set({ error: 'Chain service not initialized or no chain loaded' });
      return;
    }

    try {
      await chainService.stopExecution(chainInfo.id);
      set({ isExecuting: false });
    } catch (error) {
      const { message } = handleError(error, { chainId: chainInfo.id, action: 'stopExecution' });
      set({ error: message });
    }
  },

  updateNode: (nodeId: string, data: Partial<ChainNode>) => {
    set(state => ({
      nodes: state.nodes.map(node =>
        node.id === nodeId ? { ...node, ...data } : node
      )
    }));
  },

  updateEdge: (edgeId: string, data: Partial<ChainEdge>) => {
    set(state => ({
      edges: state.edges.map(edge =>
        edge.id === edgeId ? { ...edge, ...data } : edge
      )
    }));
  },

  addNode: (node: ChainNode) => {
    set(state => ({
      nodes: [...state.nodes, node]
    }));
  },

  addEdge: (edge: ChainEdge) => {
    set(state => ({
      edges: [...state.edges, edge]
    }));
  },

  removeNode: (nodeId: string) => {
    set(state => ({
      nodes: state.nodes.filter(node => node.id !== nodeId),
      edges: state.edges.filter(
        edge => edge.source !== nodeId && edge.target !== nodeId
      )
    }));
  },

  removeEdge: (edgeId: string) => {
    set(state => ({
      edges: state.edges.filter(edge => edge.id !== edgeId)
    }));
  },

  clearError: () => set({ error: null }),

  setSelectedNode: (node: Node | null) => {
    set({ selectedNode: node });
  },

  createEdge: (edge: ChainEdge) => {
    set(state => ({
      edges: [...state.edges, edge]
    }));
  }
})); 