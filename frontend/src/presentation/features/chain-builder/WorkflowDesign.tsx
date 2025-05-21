import React, { useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  NodeChange,
  EdgeChange,
} from 'reactflow';
import 'reactflow/dist/style.css';

// Add custom styles
const styles = {
  container: {
    width: '100%',
    height: '100%',
    backgroundColor: '#f8f8f8',
  },
  errorContainer: {
    padding: '20px',
    color: 'red',
    backgroundColor: '#fff',
    border: '1px solid red',
    borderRadius: '4px',
    margin: '20px',
  },
};

interface Props {
  nodes: Node[];
  edges: Edge[];
  onNodeSelect: (node: Node | null) => void;
  onNodeDelete: (nodeId: string) => void;
  onEdgeDelete: (edgeId: string) => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
}

const WorkflowDesign: React.FC<Props> = ({
  nodes,
  edges,
  onNodeSelect,
  onNodeDelete,
  onEdgeDelete,
  onNodesChange,
  onEdgesChange,
}) => {
  useEffect(() => {
    console.log('WorkflowDesign mounted');
    console.log('Current nodes:', nodes);
    console.log('Current edges:', edges);
  }, [nodes, edges]);

  console.log('Rendering WorkflowDesign...');

  try {
    return (
      <div style={styles.container}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={{
            input: ({ data }) => (
              <div style={{ padding: 10, background: '#fff', border: '1px solid #777', borderRadius: 5 }}>
                {data.label}
              </div>
            ),
            default: ({ data }) => (
              <div style={{ padding: 10, background: '#fff', border: '1px solid #777', borderRadius: 5 }}>
                {data.label}
              </div>
            ),
            output: ({ data }) => (
              <div style={{ padding: 10, background: '#fff', border: '1px solid #777', borderRadius: 5 }}>
                {data.label}
              </div>
            ),
          }}
          onNodeClick={(_, node) => {
            console.log('Node clicked:', node);
            onNodeSelect(node);
          }}
          onPaneClick={() => {
            console.log('Pane clicked, deselecting node');
            onNodeSelect(null);
          }}
          onNodesDelete={(nodes) => {
            console.log('Nodes deleted:', nodes);
            nodes.forEach((node) => onNodeDelete(node.id));
          }}
          onEdgesDelete={(edges) => {
            console.log('Edges deleted:', edges);
            edges.forEach((edge) => onEdgeDelete(edge.id));
          }}
          onNodesChange={(changes) => {
            console.log('Nodes changed:', changes);
            onNodesChange(changes);
          }}
          onEdgesChange={(changes) => {
            console.log('Edges changed:', changes);
            onEdgesChange(changes);
          }}
          fitView
          defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        >
          <Background color="#aaa" gap={16} />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    );
  } catch (error) {
    console.error('Error rendering WorkflowDesign:', error);
    return (
      <div style={styles.errorContainer}>
        Error rendering workflow: {error instanceof Error ? error.message : 'Unknown error'}
      </div>
    );
  }
};

export default WorkflowDesign; 