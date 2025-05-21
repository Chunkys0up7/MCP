import React, { useCallback, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
  Panel,
} from 'reactflow';
import { Box, Typography } from '@mui/material';
import 'reactflow/dist/style.css';
import type { NodeData } from '../../../infrastructure/types/node';
import MCPNode from './MCPNode';
import { ChainNode, ChainEdge } from '../../../infrastructure/types/chain';

const nodeTypes = {
  mcp: MCPNode,
};

export interface WorkflowDesignProps {
  nodes: ChainNode[];
  edges: ChainEdge[];
  onNodesChange: (nodeId: string, data: Partial<Node['data']>) => void;
  onEdgesChange: (edge: Edge) => void;
  onNodeDelete: (nodeId: string) => void;
  onEdgeDelete: (edgeId: string) => void;
  onNodeSelect: (node: Node | null) => void;
}

const WorkflowDesign: React.FC<WorkflowDesignProps> = ({
  nodes: initialNodes,
  edges: initialEdges,
  onNodesChange,
  onEdgesChange,
  onNodeDelete,
  onEdgeDelete,
  onNodeSelect,
}) => {
  const [nodes, setNodes, onNodesChangeInternal] = useNodesState(initialNodes || []);
  const [edges, setEdges, onEdgesChangeInternal] = useEdgesState(initialEdges || []);

  // Update local state when props change
  useEffect(() => {
    if (initialNodes) {
      setNodes(initialNodes);
    }
  }, [initialNodes, setNodes]);

  useEffect(() => {
    if (initialEdges) {
      setEdges(initialEdges);
    }
  }, [initialEdges, setEdges]);

  const handleNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    onNodeSelect(node);
  }, [onNodeSelect]);

  const handlePaneClick = useCallback(() => {
    onNodeSelect(null);
  }, [onNodeSelect]);

  const handleNodesChange = useCallback((changes: NodeChange[]) => {
    onNodesChangeInternal(changes);
    changes.forEach((change) => {
      if (change.type === 'remove') {
        onNodeDelete(change.id);
      } else if (change.type === 'position' && change.position) {
        const node = nodes.find(n => n.id === change.id);
        if (node) {
          onNodesChange(change.id, { position: change.position });
        }
      }
    });
  }, [onNodesChangeInternal, onNodeDelete, onNodesChange, nodes]);

  const handleEdgesChange = useCallback((changes: EdgeChange[]) => {
    onEdgesChangeInternal(changes);
    changes.forEach((change) => {
      if (change.type === 'remove') {
        onEdgeDelete(change.id);
      }
    });
  }, [onEdgesChangeInternal, onEdgeDelete]);

  const handleConnect = useCallback((connection: Connection) => {
    if (!connection.source || !connection.target) return;
    
    const newEdge: Edge = {
      id: `edge-${connection.source}-${connection.target}`,
      source: connection.source,
      target: connection.target,
      type: 'smoothstep',
      animated: true,
      style: { stroke: '#314c68' },
    };
    onEdgesChange(newEdge);
  }, [onEdgesChange]);

  return (
    <Box sx={{ width: '100%', height: '100%', bgcolor: 'background.default' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={handleConnect}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#314c68" gap={16} />
        <Controls style={{ background: 'background.paper', border: '1px solid #314c68' }} />
        <MiniMap 
          style={{ background: 'background.paper', border: '1px solid #314c68' }}
          nodeColor={(node) => {
            switch (node.data?.type) {
              case 'llm':
                return '#0b79ee';
              case 'notebook':
                return '#00bcd4';
              case 'data':
                return '#4caf50';
              default:
                return '#314c68';
            }
          }}
        />
        <Panel position="top-right">
          {nodes.length === 0 && (
            <Typography 
              variant="body2" 
              sx={{ 
                bgcolor: 'background.paper',
                p: 2,
                borderRadius: 1,
                border: '1px solid #314c68',
                color: 'text.secondary'
              }}
            >
              Drag nodes from the library to start building your chain
            </Typography>
          )}
        </Panel>
      </ReactFlow>
    </Box>
  );
};

export default WorkflowDesign; 