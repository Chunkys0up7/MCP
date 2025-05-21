import { useCallback } from 'react';
import { useChainStore } from '../state/chainStore';
import { useNotification } from '../context/NotificationContext';
import type { Node, Edge } from 'reactflow';
import type { NodeData } from '../types/node';
import type { MCPItem } from '../types/mcp';

export const useChainOperations = () => {
  const {
    nodes,
    edges,
    chainInfo,
    isLoading,
    error,
    loadChain,
    saveChain,
    executeChain,
    addNode,
    updateNode,
    removeNode,
    addEdge,
    removeEdge,
    clearError,
  } = useChainStore();

  const { showSuccess, showError } = useNotification();

  const handleLoadChain = useCallback(async (id: string) => {
    try {
      await loadChain(id);
      showSuccess('Chain loaded successfully');
    } catch (err) {
      showError('Failed to load chain');
    }
  }, [loadChain, showSuccess, showError]);

  const handleSaveChain = useCallback(async () => {
    try {
      await saveChain();
      showSuccess('Chain saved successfully');
    } catch (err) {
      showError('Failed to save chain');
    }
  }, [saveChain, showSuccess, showError]);

  const handleExecuteChain = useCallback(async () => {
    try {
      await executeChain();
      showSuccess('Chain execution started');
    } catch (err) {
      showError('Failed to execute chain');
    }
  }, [executeChain, showSuccess, showError]);

  const handleAddMCP = useCallback((mcp: MCPItem) => {
    const newNode: Node<NodeData> = {
      id: `${mcp.id}-${Date.now()}`,
      type: 'mcp',
      position: { x: 100, y: 100 },
      data: {
        label: mcp.name,
        type: mcp.type,
        status: 'idle',
        config: mcp.config,
      },
    };
    addNode(newNode);
  }, [addNode]);

  const handleUpdateNode = useCallback((nodeId: string, data: Partial<NodeData>) => {
    try {
      updateNode(nodeId, data);
      showSuccess('Node updated successfully');
    } catch (err) {
      showError('Failed to update node');
    }
  }, [updateNode, showSuccess, showError]);

  const handleRemoveNode = useCallback((nodeId: string) => {
    try {
      removeNode(nodeId);
      showSuccess('Node removed successfully');
    } catch (err) {
      showError('Failed to remove node');
    }
  }, [removeNode, showSuccess, showError]);

  const handleAddEdge = useCallback((edge: Edge) => {
    try {
      addEdge(edge);
      showSuccess('Edge added successfully');
    } catch (err) {
      showError('Failed to add edge');
    }
  }, [addEdge, showSuccess, showError]);

  const handleRemoveEdge = useCallback((edgeId: string) => {
    try {
      removeEdge(edgeId);
      showSuccess('Edge removed successfully');
    } catch (err) {
      showError('Failed to remove edge');
    }
  }, [removeEdge, showSuccess, showError]);

  return {
    nodes,
    edges,
    chainInfo,
    isLoading,
    error,
    handleLoadChain,
    handleSaveChain,
    handleExecuteChain,
    handleAddMCP,
    handleUpdateNode,
    handleRemoveNode,
    handleAddEdge,
    handleRemoveEdge,
    clearError,
  };
}; 