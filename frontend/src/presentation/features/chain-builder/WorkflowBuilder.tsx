import React from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  ReactFlowInstance,
  addEdge,
  Connection,
  applyNodeChanges,
  NodeChange,
  applyEdgeChanges,
  EdgeChange,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useFlowStore } from '../../../store/flowStore';

// Basic node types
const nodeTypes = {
  input: ({ data }: { data: { label: string } }) => (
    <div style={{ padding: 10, background: '#e6f3ff', border: '1px solid #1976d2', borderRadius: 5 }}>
      {data.label}
    </div>
  ),
  default: ({ data }: { data: { label: string } }) => (
    <div style={{ padding: 10, background: '#fff', border: '1px solid #777', borderRadius: 5 }}>
      {data.label}
    </div>
  ),
  output: ({ data }: { data: { label: string } }) => (
    <div style={{ padding: 10, background: '#ffe6e6', border: '1px solid #d32f2f', borderRadius: 5 }}>
      {data.label}
    </div>
  ),
  llm: ({ data }: { data: { label: string } }) => (
    <div style={{ padding: 10, background: '#e6f3ff', border: '2px solid #3B82F6', borderRadius: 5 }}>
      {data.label}
    </div>
  ),
  notebook: ({ data }: { data: { label: string } }) => (
    <div style={{ padding: 10, background: '#f3e8ff', border: '2px solid #8B5CF6', borderRadius: 5 }}>
      {data.label}
    </div>
  ),
  data: ({ data }: { data: { label: string } }) => (
    <div style={{ padding: 10, background: '#d1fae5', border: '2px solid #10B981', borderRadius: 5 }}>
      {data.label}
    </div>
  ),
};

const WorkflowBuilder: React.FC = () => {
  const {
    nodes,
    setNodes,
    edges,
    setEdges,
    setSelectedNode,
    setSelectedEdge,
  } = useFlowStore();

  const reactFlowWrapper = React.useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = React.useState<ReactFlowInstance | null>(null);

  // Handle node changes (e.g., position, deletion)
  const onNodesChange = React.useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );

  // Handle edge changes (e.g., deletion)
  const onEdgesChange = React.useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  // Handle new connections
  const onConnect = React.useCallback(
    (connection: Connection) => setEdges((eds) => addEdge({ ...connection, id: `edge-${+new Date()}`, label: '' }, eds)),
    [setEdges]
  );

  // Handle drag over
  const onDragOver = React.useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // Handle drop
  const onDrop = React.useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData('application/reactflow');
      if (!type || !reactFlowInstance || !reactFlowWrapper.current) return;
      const bounds = reactFlowWrapper.current.getBoundingClientRect();
      const position = reactFlowInstance.project({
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top,
      });
      const newNodeId = `${type}-${+new Date()}`;
      const newNode: Node = {
        id: newNodeId,
        type,
        position,
        data: { label: `${type.charAt(0).toUpperCase() + type.slice(1)} Node` },
      };
      setNodes((nds) => applyNodeChanges([{ type: 'add', item: newNode }], nds));
    },
    [reactFlowInstance, setNodes, setSelectedNode]
  );

  // Edge click handler
  const onEdgeClick = React.useCallback((event: React.MouseEvent, edge: Edge) => {
    event.stopPropagation();
    setSelectedEdge(edge);
    setSelectedNode(null);
  }, [setSelectedEdge, setSelectedNode]);

  // Node click handler
  const onNodeClick = React.useCallback((_: any, node: Node) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  }, [setSelectedNode, setSelectedEdge]);

  // Pane click handler
  const onPaneClick = React.useCallback(() => {
    setSelectedNode(null);
    setSelectedEdge(null);
  }, [setSelectedNode, setSelectedEdge]);

  return (
    <div ref={reactFlowWrapper} style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        deleteKeyCode={['Backspace', 'Delete']}
        fitView
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        onPaneClick={onPaneClick}
        onInit={setReactFlowInstance}
        onDrop={onDrop}
        onDragOver={onDragOver}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
};

export default WorkflowBuilder; 