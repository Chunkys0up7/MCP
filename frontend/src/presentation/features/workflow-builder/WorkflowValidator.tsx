import React from 'react';
import { Node, Edge } from 'reactflow';
import { useWorkflowStore } from '../../../infrastructure/state/workflowStore';
import { ValidationError } from './types';

export const useWorkflowValidator = () => {
  const { nodes, edges } = useWorkflowStore();

  const validateNode = (node: Node): ValidationError[] => {
    const errors: ValidationError[] = [];

    // Check required fields based on node type
    switch (node.data.type) {
      case 'llm':
        if (!node.data.model) {
          errors.push({
            type: 'node',
            id: node.id,
            message: 'LLM node must specify a model',
          });
        }
        if (node.data.temperature === undefined) {
          errors.push({
            type: 'node',
            id: node.id,
            message: 'LLM node must specify temperature',
          });
        }
        if (!node.data.maxTokens) {
          errors.push({
            type: 'node',
            id: node.id,
            message: 'LLM node must specify max tokens',
          });
        }
        break;

      case 'notebook':
        if (!node.data.notebookPath) {
          errors.push({
            type: 'node',
            id: node.id,
            message: 'Notebook node must specify a path',
          });
        }
        if (!node.data.kernel) {
          errors.push({
            type: 'node',
            id: node.id,
            message: 'Notebook node must specify a kernel',
          });
        }
        if (!node.data.timeout) {
          errors.push({
            type: 'node',
            id: node.id,
            message: 'Notebook node must specify a timeout',
          });
        }
        break;

      case 'data':
        if (!node.data.dataType) {
          errors.push({
            type: 'node',
            id: node.id,
            message: 'Data node must specify a data type',
          });
        }
        if (!node.data.source) {
          errors.push({
            type: 'node',
            id: node.id,
            message: 'Data node must specify a source',
          });
        }
        if (!node.data.format) {
          errors.push({
            type: 'node',
            id: node.id,
            message: 'Data node must specify a format',
          });
        }
        break;
    }

    return errors;
  };

  const validateEdge = (edge: Edge): ValidationError[] => {
    const errors: ValidationError[] = [];
    const sourceNode = nodes.find((n) => n.id === edge.source);
    const targetNode = nodes.find((n) => n.id === edge.target);

    if (!sourceNode || !targetNode) {
      errors.push({
        type: 'edge',
        id: edge.id,
        message: 'Edge references non-existent nodes',
      });
      return errors;
    }

    // Check for cycles
    const visited = new Set<string>();
    const path = new Set<string>();

    const hasCycle = (nodeId: string): boolean => {
      if (path.has(nodeId)) return true;
      if (visited.has(nodeId)) return false;

      visited.add(nodeId);
      path.add(nodeId);

      const outgoingEdges = edges.filter((e) => e.source === nodeId);
      for (const edge of outgoingEdges) {
        if (hasCycle(edge.target)) return true;
      }

      path.delete(nodeId);
      return false;
    };

    if (hasCycle(edge.source)) {
      errors.push({
        type: 'edge',
        id: edge.id,
        message: 'Edge creates a cycle in the workflow',
      });
    }

    return errors;
  };

  const validateWorkflow = (): ValidationError[] => {
    const errors: ValidationError[] = [];

    // Check for empty workflow
    if (nodes.length === 0) {
      errors.push({
        type: 'workflow',
        message: 'Workflow must contain at least one node',
      });
      return errors;
    }

    // Validate all nodes
    nodes.forEach((node) => {
      errors.push(...validateNode(node));
    });

    // Validate all edges
    edges.forEach((edge) => {
      errors.push(...validateEdge(edge));
    });

    // Check for disconnected nodes
    const connectedNodes = new Set<string>();
    edges.forEach((edge) => {
      connectedNodes.add(edge.source);
      connectedNodes.add(edge.target);
    });

    nodes.forEach((node) => {
      if (!connectedNodes.has(node.id)) {
        errors.push({
          type: 'node',
          id: node.id,
          message: 'Node is not connected to any other node',
        });
      }
    });

    return errors;
  };

  return {
    validateNode,
    validateEdge,
    validateWorkflow,
  };
}; 