import { create } from 'zustand';
import type { Node } from 'reactflow';
import type { ChainState, ChainNode, ChainEdge, ChainConfig, ChainInfo } from '../types';
import { ChainServiceImpl } from '../services/chainService';
import { handleError } from '../utils/errorHandling';
import { captureException } from '../monitoring/error';

interface ChainStore extends ChainState {
  setNodes: (nodes: ChainNode[]) => void;
  setEdges: (edges: ChainEdge[]) => void;
  addNode: (node: ChainNode) => void;
  updateNode: (nodeId: string, data: Record<string, unknown>) => void;
  removeNode: (nodeId: string) => void;
  addEdge: (edge: ChainEdge) => void;
  removeEdge: (edgeId: string) => void;
  clear: () => void;
  loadChain: (id: string) => Promise<void>;
  saveChain: () => Promise<void>;
  executeChain: () => Promise<void>;
  stopExecution: () => Promise<void>;
  clearError: () => void;
  setSelectedNode: (node: Node | null) => void;
}

// Initial state
const initialState: Omit<ChainState, 'chainService'> = {
  chainInfo: null,
  chainConfig: null,
  nodes: [],
  edges: [],
  isLoading: false,
  error: null,
  isExecuting: false,
  selectedNode: null
};

export const useChainStore = create<ChainStore>((set, get) => ({
  ...initialState,
  chainService: new ChainServiceImpl(import.meta.env.VITE_API_URL || 'http://localhost:3000/api'),

  setNodes: (nodes: ChainNode[]) => set({ nodes }),
  setEdges: (edges: ChainEdge[]) => set({ edges }),
  addNode: (node: ChainNode) => set((state) => ({ nodes: [...state.nodes, node] })),
  updateNode: (nodeId: string, data: Record<string, unknown>) =>
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
      ),
    })),
  removeNode: (nodeId: string) =>
    set((state) => ({
      nodes: state.nodes.filter((node) => node.id !== nodeId),
      edges: state.edges.filter(
        (edge) => edge.source !== nodeId && edge.target !== nodeId
      ),
    })),
  addEdge: (edge: ChainEdge) => set((state) => ({ edges: [...state.edges, edge] })),
  removeEdge: (edgeId: string) =>
    set((state) => ({
      edges: state.edges.filter((edge) => edge.id !== edgeId),
    })),

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

  clearError: () => set({ error: null }),
  setSelectedNode: (node: Node | null) => set({ selectedNode: node }),
  clear: () => set(initialState),
})); 