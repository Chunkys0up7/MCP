import React from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  Connection,
  addEdge,
  useNodesState,
  useEdgesState,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Box, Button } from '@mui/material';
import { useChainStore } from '../../../infrastructure/state/chainStore';
import type { NodeData } from '../../../infrastructure/types/node';
import LLMNode from './nodes/LLMNode';
import NotebookNode from './nodes/NotebookNode';
import DataNode from './nodes/DataNode';

const nodeTypes = {
  llm: LLMNode,
  notebook: NotebookNode,
  data: DataNode,
};

const ChainCanvas: React.FC = () => {
  const { nodes: storeNodes, edges: storeEdges, addNode, updateNode, removeNode, addEdge: addStoreEdge, removeEdge } = useChainStore();
  const [nodes, setNodes, onNodesChange] = useNodesState<NodeData>(storeNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(storeEdges);

  React.useEffect(() => {
    setNodes(storeNodes);
    setEdges(storeEdges);
  }, [storeNodes, storeEdges, setNodes, setEdges]);

  const onConnect = React.useCallback(
    (connection: Connection) => {
      const newEdge = addEdge(connection, edges);
      setEdges(newEdge);
      addStoreEdge({
        id: `${connection.source}-${connection.target}`,
        source: connection.source!,
        target: connection.target!,
        type: 'smoothstep',
      });
    },
    [edges, setEdges, addStoreEdge]
  );

  const onNodeDragStop = React.useCallback(
    (_: React.MouseEvent, node: Node<NodeData>) => {
      updateNode(node.id, { position: node.position });
    },
    [updateNode]
  );

  const onNodeDelete = React.useCallback(
    (nodesToDelete: Node<NodeData>[]) => {
      nodesToDelete.forEach((node) => {
        removeNode(node.id);
      });
    },
    [removeNode]
  );

  const onEdgeDelete = React.useCallback(
    (edgesToDelete: Edge[]) => {
      edgesToDelete.forEach((edge) => {
        removeEdge(edge.id);
      });
    },
    [removeEdge]
  );

  const handleAddNode = (type: keyof typeof nodeTypes) => {
    const newNode: Node<NodeData> = {
      id: `${type}-${Date.now()}`,
      type,
      position: { x: 100, y: 100 },
      data: {
        label: `New ${type} Node`,
        type,
        status: 'idle',
        config: undefined,
      },
    };
    addNode(newNode);
  };

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDragStop={onNodeDragStop}
        onNodesDelete={onNodeDelete}
        onEdgesDelete={onEdgeDelete}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
        <Panel position="top-left">
          <Box sx={{ display: 'flex', gap: 1, p: 1, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Button
              variant="contained"
              size="small"
              onClick={() => handleAddNode('llm')}
              aria-label="Add LLM Node"
            >
              Add LLM
            </Button>
            <Button
              variant="contained"
              size="small"
              onClick={() => handleAddNode('notebook')}
              aria-label="Add Notebook Node"
            >
              Add Notebook
            </Button>
            <Button
              variant="contained"
              size="small"
              onClick={() => handleAddNode('data')}
              aria-label="Add Data Node"
            >
              Add Data
            </Button>
          </Box>
        </Panel>
      </ReactFlow>
    </Box>
  );
};

export default ChainCanvas; 