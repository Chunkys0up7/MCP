import React, { useCallback, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Box, Paper, Typography } from '@mui/material';
import { MCPNode } from './MCPNode';
import { MCPLibrary } from './MCPLibrary';
import { PropertiesPanel } from './PropertiesPanel';

const nodeTypes = {
  mcp: MCPNode,
};

const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

export const ChainCanvas: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge(params, eds));
    },
    [setEdges]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  return (
    <Box sx={{ display: 'flex', height: '100vh', width: '100vw' }}>
      {/* MCP Library Panel */}
      <Paper
        sx={{
          width: 300,
          p: 2,
          borderRight: 1,
          borderColor: 'divider',
          overflow: 'auto',
        }}
      >
        <MCPLibrary onDragStart={(event, nodeType) => {
          event.dataTransfer.setData('application/reactflow', nodeType);
          event.dataTransfer.effectAllowed = 'move';
        }} />
      </Paper>

      {/* Main Canvas */}
      <Box sx={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
          <Panel position="top-right">
            <Typography variant="h6">MCP Chain Builder</Typography>
          </Panel>
        </ReactFlow>
      </Box>

      {/* Properties Panel */}
      {selectedNode && (
        <Paper
          sx={{
            width: 300,
            p: 2,
            borderLeft: 1,
            borderColor: 'divider',
            overflow: 'auto',
          }}
        >
          <PropertiesPanel node={selectedNode} />
        </Paper>
      )}
    </Box>
  );
}; 