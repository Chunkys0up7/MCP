import React, { useCallback, useRef, useImperativeHandle, forwardRef, useEffect } from 'react';
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState, Node, Edge, useReactFlow, NodeChange, EdgeChange } from 'reactflow';
import 'reactflow/dist/style.css';
import { useNotification } from '../../infrastructure/context/NotificationContext';

interface CanvasProps {
  onNodeSelect: (node: Node | null) => void;
  onEdgeSelect: (edge: Edge | null) => void;
  onNodesUpdate?: (nodes: Node[]) => void;
  onEdgesUpdate?: (edges: Edge[]) => void;
}

const initialNodes = [
  {
    id: '1',
    type: 'default',
    position: { x: 100, y: 150 },
    data: { label: 'Data Loader' },
  },
  {
    id: '2',
    type: 'default',
    position: { x: 350, y: 150 },
    data: { label: 'LLM Summarizer' },
  },
  {
    id: '3',
    type: 'default',
    position: { x: 600, y: 150 },
    data: { label: 'Text Output' },
  },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', label: 'text_content' },
  { id: 'e2-3', source: '2', target: '3', label: 'summary' },
];

const Canvas = forwardRef<any, CanvasProps>(({ onNodeSelect, onEdgeSelect, onNodesUpdate, onEdgesUpdate }, ref) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const nodeIdRef = useRef(4);
  const { zoomIn: rfZoomIn, zoomOut: rfZoomOut, fitView } = useReactFlow();
  const { showSuccess, showError } = useNotification();

  // Sync nodes/edges to parent
  useEffect(() => {
    if (onNodesUpdate) onNodesUpdate(nodes);
  }, [nodes, onNodesUpdate]);
  useEffect(() => {
    if (onEdgesUpdate) onEdgesUpdate(edges);
  }, [edges, onEdgesUpdate]);

  // Simple undo/redo stack
  const history = useRef<{ nodes: Node[]; edges: Edge[] }[]>([]);
  const future = useRef<{ nodes: Node[]; edges: Edge[] }[]>([]);

  // Save state to history on change
  const pushHistory = (nodes: Node[], edges: Edge[]) => {
    history.current.push({ nodes: JSON.parse(JSON.stringify(nodes)), edges: JSON.parse(JSON.stringify(edges)) });
    if (history.current.length > 50) history.current.shift();
    future.current = [];
  };

  const onNodesChangeWithHistory = useCallback((changes: NodeChange[]) => {
    pushHistory(nodes, edges);
    onNodesChange(changes);
    if (changes.some(change => change.type === 'remove')) {
      showSuccess('Node deleted');
    }
  }, [nodes, edges, onNodesChange]);

  const onEdgesChangeWithHistory = useCallback((changes: EdgeChange[]) => {
    pushHistory(nodes, edges);
    onEdgesChange(changes);
    if (changes.some(change => change.type === 'remove')) {
      showSuccess('Edge deleted');
    }
  }, [nodes, edges, onEdgesChange]);

  // Expose methods to parent
  useImperativeHandle(ref, () => ({
    zoomIn: () => rfZoomIn(),
    zoomOut: () => rfZoomOut(),
    undo: () => {
      if (history.current.length > 0) {
        const prev = history.current.pop();
        if (prev) {
          future.current.push({ nodes, edges });
          setNodes(prev.nodes);
          setEdges(prev.edges);
          showSuccess('Undo successful');
        }
      }
    },
    redo: () => {
      if (future.current.length > 0) {
        const next = future.current.pop();
        if (next) {
          pushHistory(nodes, edges);
          setNodes(next.nodes);
          setEdges(next.edges);
          showSuccess('Redo successful');
        }
      }
    },
    updateNodeLabel: (id: string, label: string) => {
      setNodes((nds) => nds.map((n) => n.id === id ? { ...n, data: { ...n.data, label } } : n));
      showSuccess('Node label updated');
    },
    updateEdgeLabel: (id: string, label: string) => {
      setEdges((eds) => eds.map((e) => e.id === id ? { ...e, label } : e));
      showSuccess('Edge label updated');
    },
    getWorkflow: () => ({ nodes, edges }),
    addNode: (node: Node) => {
      setNodes((nds) => nds.concat(node));
      showSuccess('Node added');
    },
  }));

  const onDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
    const type = event.dataTransfer.getData('application/reactflow');
    if (!type || !reactFlowBounds) return;
    const position = {
      x: event.clientX - reactFlowBounds.left,
      y: event.clientY - reactFlowBounds.top,
    };
    const newNode: Node = {
      id: `${nodeIdRef.current++}`,
      type: 'default',
      position,
      data: { label: type },
    };
    setNodes((nds) => nds.concat(newNode));
    pushHistory([...nodes, newNode], edges);
  }, [setNodes, nodes, edges]);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onNodeClick = useCallback((_: any, node: Node) => {
    onNodeSelect(node);
    onEdgeSelect(null);
  }, [onNodeSelect, onEdgeSelect]);

  const onEdgeClick = useCallback((_: any, edge: Edge) => {
    onEdgeSelect(edge);
    onNodeSelect(null);
  }, [onNodeSelect, onEdgeSelect]);

  const onPaneClick = useCallback(() => {
    onNodeSelect(null);
    onEdgeSelect(null);
  }, [onNodeSelect, onEdgeSelect]);

  return (
    <div
      ref={reactFlowWrapper}
      style={{ flex: 1, height: '100%' }}
      tabIndex={0}
      role="region"
      aria-label="Workflow Canvas"
      aria-describedby="canvas-instructions"
      onFocus={e => e.currentTarget.style.outline = '2px solid #1976d2'}
      onBlur={e => e.currentTarget.style.outline = 'none'}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChangeWithHistory}
        onEdgesChange={onEdgesChangeWithHistory}
        onDrop={onDrop}
        onDragOver={onDragOver}
        fitView
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        onPaneClick={onPaneClick}
      >
        <Background />
        <MiniMap />
        <Controls />
      </ReactFlow>
      <div id="canvas-instructions" style={{ position: 'absolute', left: -9999, top: 'auto', width: 1, height: 1, overflow: 'hidden' }}>
        Use mouse or keyboard to interact with the workflow. (Future: Custom keyboard navigation for node/edge selection.)
      </div>
    </div>
  );
});

export default Canvas; 