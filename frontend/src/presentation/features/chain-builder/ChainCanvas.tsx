import React, { useCallback, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
} from 'reactflow';
import type { NodeProps, Connection, Edge, Node } from 'reactflow';
import 'reactflow/dist/style.css';
import { useChainStore } from '../../../infrastructure/state/chainStore';
import { Box } from '@mui/material';
import BaseNode from './nodes/BaseNode';

const nodeTypes = {
  default: BaseNode,
};

const validateConnection = (connection: Connection) => {
  // Get source and target nodes
  const sourceNode = document.querySelector(`[data-id="${connection.source}"]`);
  const targetNode = document.querySelector(`[data-id="${connection.target}"]`);

  if (!sourceNode || !targetNode) return false;

  // Get node types
  const sourceType = sourceNode.getAttribute('data-type');
  const targetType = targetNode.getAttribute('data-type');

  // Validate connection based on node types
  if (sourceType === 'data' && targetType === 'data') return false; // Data nodes can't connect to data nodes
  if (sourceType === 'llm' && targetType === 'llm') return false; // LLM nodes can't connect to LLM nodes
  if (sourceType === 'notebook' && targetType === 'notebook') return false; // Notebook nodes can't connect to notebook nodes

  return true;
};

const ChainCanvas: React.FC = () => {
  const { nodes: storeNodes, edges: storeEdges, addNode, createEdge, setSelectedNode, selectedNode } = useChainStore();
  const [nodes, , onNodesChange] = useNodesState(storeNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(storeEdges);

  const onConnect = useCallback(
    (params: Connection | Edge) => {
      if (validateConnection(params as Connection)) {
        createEdge(params as Edge);
        setEdges((eds) => addEdge(params, eds));
      }
    },
    [createEdge, setEdges]
  );

  const onNodeDragStop = useCallback(
    (event: React.MouseEvent, node: Node) => {
      addNode(node);
    },
    [addNode]
  );

  const onNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      setSelectedNode(node);
    },
    [setSelectedNode]
  );

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, [setSelectedNode]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!selectedNode) return;

      const selectedIndex = nodes.findIndex(node => node.id === selectedNode.id);
      if (selectedIndex === -1) return;

      let nextNode: Node | null = null;

      switch (event.key) {
        case 'ArrowUp':
          // Find the closest node above
          nextNode = nodes
            .filter(node => node.position.y < selectedNode.position.y)
            .sort((a, b) => b.position.y - a.position.y)[0];
          break;
        case 'ArrowDown':
          // Find the closest node below
          nextNode = nodes
            .filter(node => node.position.y > selectedNode.position.y)
            .sort((a, b) => a.position.y - b.position.y)[0];
          break;
        case 'ArrowLeft':
          // Find the closest node to the left
          nextNode = nodes
            .filter(node => node.position.x < selectedNode.position.x)
            .sort((a, b) => b.position.x - a.position.x)[0];
          break;
        case 'ArrowRight':
          // Find the closest node to the right
          nextNode = nodes
            .filter(node => node.position.x > selectedNode.position.x)
            .sort((a, b) => a.position.x - b.position.x)[0];
          break;
        case 'Escape':
          setSelectedNode(null);
          return;
        case 'Delete':
          // TODO: Implement node deletion
          return;
      }

      if (nextNode) {
        setSelectedNode(nextNode);
        // Ensure the node is visible in the viewport
        const nodeElement = document.querySelector(`[data-id="${nextNode.id}"]`);
        if (nodeElement) {
          nodeElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedNode, nodes, setSelectedNode]);

  return (
    <Box 
      sx={{ width: '100%', height: '100%', bgcolor: 'background.default' }}
      role="application"
      aria-label="Chain Builder Canvas"
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDragStop={onNodeDragStop}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        defaultEdgeOptions={{
          style: { stroke: '#b1b1b7' },
          animated: true,
        }}
      >
        <Background color="#aaa" gap={16} />
        <Controls />
        <MiniMap 
          nodeColor={(node) => {
            switch (node.type) {
              case 'llm': return '#3B82F6';
              case 'notebook': return '#8B5CF6';
              case 'data': return '#10B981';
              default: return '#eee';
            }
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </Box>
  );
};

export default ChainCanvas; 