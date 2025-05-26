import React, { useState } from 'react';
import { ComponentSummary } from '../../services/api';

interface DependencyNode {
  id: string;
  label: string;
  type: string;
}

interface DependencyEdge {
  from: string;
  to: string;
}

interface ComponentDetailViewProps {
  component: ComponentSummary;
  onClose: () => void;
  dependencies?: {
    nodes: DependencyNode[];
    edges: DependencyEdge[];
  };
}

const tabs = ['Overview', 'Dependencies', 'Sandbox', 'Versions', 'Reviews'];

// Robust mock dependency data
const mockDependencies = {
  nodes: [
    { id: 'comp1', label: 'GPT-4 Turbo', type: 'LLM' },
    { id: 'comp2', label: 'Data Validator', type: 'Data' },
    { id: 'comp3', label: 'Preprocessor', type: 'Utility' },
    { id: 'comp4', label: 'Notebook Runner', type: 'Notebook' },
    { id: 'comp5', label: 'Output Formatter', type: 'Utility' },
  ],
  edges: [
    { from: 'comp2', to: 'comp1' }, // Data Validator feeds into GPT-4 Turbo
    { from: 'comp3', to: 'comp2' }, // Preprocessor feeds into Data Validator
    { from: 'comp4', to: 'comp3' }, // Notebook Runner feeds into Preprocessor
    { from: 'comp1', to: 'comp5' }, // GPT-4 Turbo feeds into Output Formatter
  ],
};

const DependencyVisualizer: React.FC<{ nodes: DependencyNode[]; edges: DependencyEdge[] }> = ({ nodes, edges }) => {
  // Simple SVG graph visualization (horizontal layout)
  const nodePositions = nodes.reduce<{ [id: string]: { x: number; y: number } }>((acc, node, idx) => {
    acc[node.id] = { x: 60 + idx * 120, y: 60 };
    return acc;
  }, {});
  return (
    <svg width={nodes.length * 140} height={160} style={{ background: '#f9fafb', borderRadius: 8 }}>
      {/* Edges */}
      {edges.map((edge, i) => {
        const from = nodePositions[edge.from];
        const to = nodePositions[edge.to];
        if (!from || !to) return null;
        return (
          <line
            key={i}
            x1={from.x + 40}
            y1={from.y + 20}
            x2={to.x}
            y2={to.y + 20}
            stroke="#6366f1"
            strokeWidth={2}
            markerEnd="url(#arrowhead)"
          />
        );
      })}
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#6366f1" />
        </marker>
      </defs>
      {/* Nodes */}
      {nodes.map((node) => (
        <g key={node.id}>
          <rect
            x={nodePositions[node.id].x}
            y={nodePositions[node.id].y}
            width={80}
            height={40}
            rx={8}
            fill="#fff"
            stroke="#6366f1"
            strokeWidth={2}
            filter="url(#shadow)"
          />
          <text
            x={nodePositions[node.id].x + 40}
            y={nodePositions[node.id].y + 25}
            textAnchor="middle"
            fontSize={13}
            fill="#222"
          >
            {node.label}
          </text>
          <text
            x={nodePositions[node.id].x + 40}
            y={nodePositions[node.id].y + 38}
            textAnchor="middle"
            fontSize={10}
            fill="#6366f1"
          >
            {node.type}
          </text>
        </g>
      ))}
    </svg>
  );
};

const ComponentDetailView: React.FC<ComponentDetailViewProps> = ({ component, onClose, dependencies }) => {
  const [activeTab, setActiveTab] = useState('Overview');
  const deps = dependencies || mockDependencies;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      width: 400,
      height: '100%',
      background: '#fff',
      boxShadow: '-2px 0 8px rgba(0,0,0,0.08)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
    }}>
      <div style={{ padding: 16, borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0 }}>{component.name}</h3>
        <button onClick={onClose} style={{ fontSize: 18, background: 'none', border: 'none', cursor: 'pointer' }}>×</button>
      </div>
      <div style={{ display: 'flex', borderBottom: '1px solid #eee' }}>
        {tabs.map(tab => (
          <div
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              flex: 1,
              padding: '12px 0',
              textAlign: 'center',
              cursor: 'pointer',
              background: activeTab === tab ? '#f3f4f6' : 'transparent',
              fontWeight: activeTab === tab ? 600 : 400,
              borderBottom: activeTab === tab ? '2px solid #6366f1' : 'none',
            }}
          >
            {tab}
          </div>
        ))}
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
        {/* Placeholder content for each tab */}
        {activeTab === 'Overview' && (
          <div>
            <h4>Overview</h4>
            <p>{component.description}</p>
            <div>Type: {component.type}</div>
            <div>Version: {component.version}</div>
            <div>Tags: {component.tags?.join(', ')}</div>
          </div>
        )}
        {activeTab === 'Dependencies' && (
          <div>
            <h4>Dependencies</h4>
            <DependencyVisualizer nodes={deps.nodes} edges={deps.edges} />
          </div>
        )}
        {activeTab === 'Sandbox' && (
          <div>
            <h4>Sandbox</h4>
            <p>Sandbox UI for testing the component will go here.</p>
          </div>
        )}
        {activeTab === 'Versions' && (
          <div>
            <h4>Versions</h4>
            <p>Version history and changelogs will go here.</p>
          </div>
        )}
        {activeTab === 'Reviews' && (
          <div>
            <h4>Reviews</h4>
            <p>User reviews and usage stats will go here.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComponentDetailView; 