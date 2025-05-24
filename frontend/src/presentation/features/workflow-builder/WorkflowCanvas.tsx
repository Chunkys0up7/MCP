import React, { useCallback, useRef, useState, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  ReactFlowInstance,
  NodeChange,
  EdgeChange,
  Connection,
  Panel,
  applyNodeChanges,
  applyEdgeChanges,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Box, Drawer } from '@mui/material';
import { useWorkflowStore } from '../../../infrastructure/state/workflowStore';
import { MCPNode } from './nodes/MCPNode';
import { InputNode } from './nodes/InputNode';
import { OutputNode } from './nodes/OutputNode';
import { DataNode } from './nodes/DataNode';
import { NotebookNode } from './nodes/NotebookNode';
import { LLMNode } from './nodes/LLMNode';
import { NodeConfigPanel } from './NodeConfigPanel';
import { NodePalette } from './NodePalette';
import { ValidationPanel } from './ValidationPanel';
import { ExecutionPanel } from './ExecutionPanel';
import { ExecutionMonitor } from './ExecutionMonitor';
import { WorkflowExecutionStatus } from '../../../domain/models/workflow';
import { useWorkflowValidation } from '../../../application/hooks/useWorkflowValidation';
import { ErrorPanel } from './ErrorPanel';
import { useErrorHandling } from '../../../application/hooks/useErrorHandling';
import { PerformancePanel } from './PerformancePanel';
import { usePerformance } from '../../../application/hooks/usePerformance';
import { OptimizationPanel } from './OptimizationPanel';
import { ExecutionStatus } from './ExecutionStatus';
import { SandboxPreview } from './SandboxPreview';

interface WorkflowCanvasProps {
  workflowId: string;
  onSave?: () => void;
  onValidationChange?: (isValid: boolean) => void;
}

const nodeTypes = {
  mcp: MCPNode,
  input: InputNode,
  output: OutputNode,
  data: DataNode,
  notebook: NotebookNode,
  llm: LLMNode,
};

export const WorkflowCanvas: React.FC<WorkflowCanvasProps> = ({
  workflowId,
  onSave,
  onValidationChange
}) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const { nodes, edges, setNodes, setEdges, updateNodeData, updateEdgeLabel } = useWorkflowStore();
  const { isValid } = useWorkflowValidation(nodes, edges);
  const { handleError } = useErrorHandling(nodes, edges);
  const {
    trackNodeExecution,
    trackNetworkRequest,
    getCachedResult,
    setCachedResult
  } = usePerformance(workflowId, nodes, edges);

  useEffect(() => {
    onValidationChange?.(isValid);
  }, [isValid, onValidationChange]);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      setNodes(applyNodeChanges(changes, nodes));
      changes.forEach((change) => {
        if (change.type === 'position' && change.dragging === false) {
          updateNodeData(change.id, { position: change.position });
        }
      });
    },
    [setNodes, updateNodeData, nodes]
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      setEdges(applyEdgeChanges(changes, edges));
    },
    [setEdges, edges]
  );

  const onConnect = useCallback(
    (params: Connection) => {
      if (params.source && params.target) {
        setEdges([
          ...edges,
          {
            ...params,
            id: `edge-${Date.now()}`,
            source: params.source,
            target: params.target,
            sourceHandle: params.sourceHandle ?? undefined,
            targetHandle: params.targetHandle ?? undefined,
          } as Edge,
        ]);
      }
    },
    [setEdges, edges]
  );

  const onDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');
      const position = reactFlowInstance?.project({
        x: event.clientX - (reactFlowBounds?.left || 0),
        y: event.clientY - (reactFlowBounds?.top || 0),
      });

      if (typeof type === 'undefined' || !type || !position) {
        return;
      }

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: { label: `${type} node` },
      };

      setNodes([...nodes, newNode]);
    },
    [reactFlowInstance, setNodes, nodes]
  );

  const onNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      setSelectedNode(node);
    },
    []
  );

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const handleCloseConfig = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const onNodeError = useCallback((nodeId: string, error: any) => {
    handleError({
      type: 'node-error',
      message: error.message || 'Node execution failed',
      severity: 'error',
      nodeId,
      details: {
        message: error.message,
        stack: error.stack,
        context: { nodeId }
      },
      maxRetries: 3
    });
  }, [handleError]);

  const onStepError = useCallback((stepId: string, error: any) => {
    handleError({
      type: 'step-error',
      message: error.message || 'Step execution failed',
      severity: 'error',
      stepId,
      details: {
        message: error.message,
        stack: error.stack,
        context: { stepId }
      },
      maxRetries: 3
    });
  }, [handleError]);

  const onNodeExecution = useCallback(async (nodeId: string, result: any) => {
    const startTime = performance.now();
    try {
      // Check cache first
      const cachedResult = await getCachedResult(nodeId);
      if (cachedResult) {
        return cachedResult;
      }

      // Execute node logic here
      // ... existing node execution code ...

      // Cache the result
      await setCachedResult(nodeId, result, {
        ttl: 5 * 60 * 1000, // 5 minutes
        metadata: { timestamp: Date.now() }
      });

      return result;
    } finally {
      const executionTime = performance.now() - startTime;
      trackNodeExecution(nodeId, executionTime);
    }
  }, [getCachedResult, setCachedResult, trackNodeExecution]);

  const onNetworkRequest = useCallback(async (nodeId: string, request: () => Promise<any>) => {
    const startTime = performance.now();
    try {
      const result = await request();
      const latency = performance.now() - startTime;
      trackNetworkRequest(nodeId, latency, JSON.stringify(result).length);
      return result;
    } catch (error) {
      const latency = performance.now() - startTime;
      trackNetworkRequest(nodeId, latency, 0);
      throw error;
    }
  }, [trackNetworkRequest]);

  return (
    <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
      <ExecutionMonitor
        workflowId={workflowId}
        onExecutionComplete={(status) => {
          if (status === 'COMPLETED') {
            console.log('Workflow execution completed successfully');
          } else if (status === 'FAILED') {
            console.error('Workflow execution failed');
          }
        }}
        onStepError={onStepError}
      />
      <Box sx={{ flex: 1, position: 'relative' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background />
          <Panel position="top-right">
            <ValidationPanel />
          </Panel>
          <Panel position="top-left">
            <ExecutionStatus workflowId={workflowId} />
          </Panel>
          <Panel position="bottom-right">
            <SandboxPreview workflowId={workflowId} />
          </Panel>
        </ReactFlow>
      </Box>
      <NodePalette />
      <ErrorPanel />
      <OptimizationPanel />
      <PerformancePanel workflowId={workflowId} />
      <Drawer
        anchor="right"
        open={!!selectedNode}
        onClose={handleCloseConfig}
        sx={{
          '& .MuiDrawer-paper': {
            width: 400,
            boxSizing: 'border-box',
          },
        }}
      >
        {selectedNode && (
          <NodeConfigPanel
            node={selectedNode}
            onClose={handleCloseConfig}
            onError={(error) => onNodeError(selectedNode.id, error)}
          />
        )}
      </Drawer>
    </Box>
  );
}; 