import React, { useState } from 'react';
import { ComponentSummary } from '../../services/api';
import Card from '../common/Card';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

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
    <svg width={nodes.length * 140} height={160} style={{ background: '#f9fafb', borderRadius: 8 }} role="img" aria-label="Dependency Graph">
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
  const [activeTab, setActiveTab] = useState(0);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const deps = dependencies || mockDependencies;

  const handleAddToWorkflow = () => {
    setActionMessage('Component added to workflow (mock action).');
    setTimeout(() => setActionMessage(null), 2000);
  };
  const handleTestInSandbox = () => {
    setActionMessage('Sandbox test started (mock action).');
    setTimeout(() => setActionMessage(null), 2000);
  };

  return (
    <Box sx={{ position: 'fixed', top: 0, right: 0, width: 400, height: '100%', zIndex: 1000, display: 'flex', flexDirection: 'column', bgcolor: 'background.paper', boxShadow: 4 }}>
      <Card sx={{ borderRadius: 0, height: '100%', display: 'flex', flexDirection: 'column', p: 0 }} title={component.name}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h5" fontWeight={600}>{component.name}</Typography>
          <IconButton onClick={onClose} aria-label="Close details panel">
            <CloseIcon />
          </IconButton>
        </Box>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} variant="fullWidth" sx={{ borderBottom: 1, borderColor: 'divider' }}>
          {tabs.map((tab, idx) => <Tab key={tab} label={tab} />)}
        </Tabs>
        <Box sx={{ flex: 1, overflowY: 'auto', p: 3 }}>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>Overview</Typography>
              <Typography variant="body1" mb={2}>{component.description}</Typography>
              <Typography variant="body2" color="text.secondary">Type: {component.type}</Typography>
              <Typography variant="body2" color="text.secondary">Version: {component.version}</Typography>
              <Typography variant="body2" color="text.secondary">Tags: {component.tags?.join(', ')}</Typography>
              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button variant="contained" color="primary" onClick={handleAddToWorkflow}>Add to Workflow</Button>
                <Button variant="outlined" color="primary" onClick={handleTestInSandbox}>Test in Sandbox</Button>
              </Box>
              {actionMessage && (
                <Typography sx={{ mt: 2 }} color="success.main">{actionMessage}</Typography>
              )}
            </Box>
          )}
          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>Dependencies</Typography>
              <DependencyVisualizer nodes={deps.nodes} edges={deps.edges} />
            </Box>
          )}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>Sandbox</Typography>
              <Typography variant="body2">Sandbox UI for testing the component will go here.</Typography>
            </Box>
          )}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>Versions</Typography>
              <Typography variant="body2">Version history and changelogs will go here.</Typography>
            </Box>
          )}
          {activeTab === 4 && (
            <Box>
              <Typography variant="h6" gutterBottom>Reviews</Typography>
              <Typography variant="body2">User reviews and usage stats will go here.</Typography>
            </Box>
          )}
        </Box>
      </Card>
    </Box>
  );
};

export default ComponentDetailView; 