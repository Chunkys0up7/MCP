import { create } from 'zustand';
import type { Node, Edge } from 'reactflow';
import * as flowApi from '../services/flowApi';
import { notify } from '../services/notificationService';

type Updater<T> = T | ((prev: T) => T);

interface FlowState {
  nodes: Node[];
  edges: Edge[];
  selectedNode: Node | null;
  selectedEdge: Edge | null;
  setNodes: (nodes: Updater<Node[]>) => void;
  setEdges: (edges: Updater<Edge[]>) => void;
  setSelectedNode: (node: Node | null) => void;
  setSelectedEdge: (edge: Edge | null) => void;
  updateNodeData: (nodeId: string, data: Partial<Node['data']>) => void;
  updateEdgeLabel: (edgeId: string, label: string) => void;
  // Backend integration
  loading: boolean;
  error: string | null;
  logs: string[];
  loadWorkflowFromApi: (id: string) => Promise<void>;
  saveWorkflowToApi: (id: string) => Promise<void>;
  executeWorkflowFromApi: (id: string) => Promise<void>;
}

export const useFlowStore = create<FlowState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNode: null,
  selectedEdge: null,
  setNodes: (nodes) => set((state) => ({ nodes: typeof nodes === 'function' ? (nodes as (prev: Node[]) => Node[])(state.nodes) : nodes })),
  setEdges: (edges) => set((state) => ({ edges: typeof edges === 'function' ? (edges as (prev: Edge[]) => Edge[])(state.edges) : edges })),
  setSelectedNode: (node) => set({ selectedNode: node, selectedEdge: null }),
  setSelectedEdge: (edge) => set({ selectedEdge: edge, selectedNode: null }),
  updateNodeData: (nodeId, data) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, ...data } } : n
      ),
      selectedNode:
        state.selectedNode && state.selectedNode.id === nodeId
          ? { ...state.selectedNode, data: { ...state.selectedNode.data, ...data } }
          : state.selectedNode,
    })),
  updateEdgeLabel: (edgeId, label) =>
    set((state) => ({
      edges: state.edges.map((e) =>
        e.id === edgeId ? { ...e, label } : e
      ),
      selectedEdge:
        state.selectedEdge && state.selectedEdge.id === edgeId
          ? { ...state.selectedEdge, label }
          : state.selectedEdge,
    })),
  // Backend integration
  loading: false,
  error: null,
  logs: [],
  loadWorkflowFromApi: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const { nodes, edges } = await flowApi.loadWorkflow(id);
      set({ nodes, edges, loading: false });
      notify.success(`Workflow '${id}' loaded successfully.`);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to load workflow';
      set({ error: errorMessage, loading: false });
      notify.error(`Load failed: ${errorMessage}`);
    }
  },
  saveWorkflowToApi: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const { nodes, edges } = get();
      await flowApi.saveWorkflow(id, nodes, edges);
      set({ loading: false });
      notify.success(`Workflow '${id}' saved successfully.`);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to save workflow';
      set({ error: errorMessage, loading: false });
      notify.error(`Save failed: ${errorMessage}`);
    }
  },
  executeWorkflowFromApi: async (id: string) => {
    set({ loading: true, error: null, logs: [] });
    try {
      const { logs, result } = await flowApi.executeWorkflow(id);
      set({ logs, loading: false });
      notify.success(`Workflow '${id}' executed successfully.`);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to execute workflow';
      set({ error: errorMessage, loading: false });
      notify.error(`Execution failed: ${errorMessage}`);
    }
  },
})); 