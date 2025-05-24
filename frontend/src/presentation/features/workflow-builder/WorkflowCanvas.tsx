import React, { useCallback, useRef, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  ReactFlowInstance,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Panel,
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

const nodeTypes = {
  mcp: MCPNode,
  input: InputNode,
  output: OutputNode,
  data: DataNode,
  notebook: NotebookNode,
  llm: LLMNode,
};

export const WorkflowCanvas: React.FC = () => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const { nodes, edges, setNodes, setEdges, updateNodeData, updateEdgeLabel } = useWorkflowStore();

  const onNodesChange = useCallback(
    (changes: any) => {
      setNodes((nds) => {
        const updatedNodes = changes.reduce((acc: Node[], change: any) => {
          if (change.type === 'position' && change.dragging === false) {
            const node = nds.find((n) => n.id === change.id);
            if (node) {
              updateNodeData(change.id, { position: change.position });
            }
          }
          return acc;
        }, []);
        return updatedNodes.length > 0 ? updatedNodes : nds;
      });
    },
    [setNodes, updateNodeData]
  );

  const onEdgesChange = useCallback(
    (changes: any) => {
      setEdges((eds) => {
        const updatedEdges = changes.reduce((acc: Edge[], change: any) => {
          if (change.type === 'label') {
            const edge = eds.find((e) => e.id === change.id);
            if (edge) {
              updateEdgeLabel(change.id, change.label);
            }
          }
          return acc;
        }, []);
        return updatedEdges.length > 0 ? updatedEdges : eds;
      });
    },
    [setEdges, updateEdgeLabel]
  );

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge(params, eds));
    },
    [setEdges]
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

      setNodes((nds) => [...nds, newNode]);
    },
    [reactFlowInstance, setNodes]
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

  return (
    <Box sx={{ width: '100%', height: '100vh', display: 'flex' }}>
      <NodePalette />
      <Box ref={reactFlowWrapper} sx={{ flex: 1 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
          <Panel position="top-center">
            <Box sx={{ bgcolor: 'background.paper', p: 1, borderRadius: 1 }}>
              Workflow Builder
            </Box>
          </Panel>
          <ValidationPanel />
        </ReactFlow>
      </Box>
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
        {selectedNode && <NodeConfigPanel node={selectedNode} onClose={handleCloseConfig} />}
      </Drawer>
    </Box>
  );
}; 