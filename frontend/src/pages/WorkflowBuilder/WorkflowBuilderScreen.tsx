import React, { useState, useRef } from 'react';
import { Box, Grid, Paper, Button, TextField, CircularProgress, Alert, Stack } from '@mui/material';
import { theme } from '../../presentation/design-system/theme';
import Palette from './Palette';
import Canvas from './Canvas';
import { Node, Edge } from 'reactflow';
import SaveIcon from '@mui/icons-material/Save';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import UndoIcon from '@mui/icons-material/Undo';
import RedoIcon from '@mui/icons-material/Redo';
import { useNotification } from '../../infrastructure/context/NotificationContext';

const WorkflowBuilderScreen: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const [nodeLabel, setNodeLabel] = useState('');
  const [edgeLabel, setEdgeLabel] = useState('');
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [isLoading] = useState(false); // Future: set true when loading workflow
  const [error] = useState<string | null>(null); // Future: set error message on failure
  const canvasRef = useRef<any>(null);
  const { showSuccess, showError, showInfo } = useNotification();

  // Sync nodes/edges from Canvas
  const handleNodesUpdate = (newNodes: Node[]) => setNodes(newNodes);
  const handleEdgesUpdate = (newEdges: Edge[]) => setEdges(newEdges);

  // Update label fields when selection changes
  React.useEffect(() => {
    setNodeLabel(String(selectedNode?.data?.label || ''));
  }, [selectedNode]);
  React.useEffect(() => {
    setEdgeLabel(String(selectedEdge?.label || ''));
  }, [selectedEdge]);

  // Handlers to update node/edge label in Canvas
  const handleNodeLabelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNodeLabel(e.target.value);
    if (selectedNode && canvasRef.current?.updateNodeLabel) {
      canvasRef.current.updateNodeLabel(selectedNode.id, e.target.value);
    }
  };
  const handleEdgeLabelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEdgeLabel(e.target.value);
    if (selectedEdge && canvasRef.current?.updateEdgeLabel) {
      canvasRef.current.updateEdgeLabel(selectedEdge.id, e.target.value);
    }
  };

  // Save, Validate, Run logic
  const handleSave = () => {
    try {
      if (canvasRef.current?.getWorkflow) {
        // Simulate save
        showSuccess('Workflow saved successfully!');
        // console.log('Saving workflow:', wf);
      } else {
        // console.log('Saving workflow:', { nodes, edges });
        showSuccess('Workflow saved successfully!');
      }
      // TODO: Integrate with backend
    } catch (err) {
      showError('Failed to save workflow.');
    }
  };
  const handleValidate = () => {
    // Placeholder: check for disconnected nodes
    const nodeIds = new Set(nodes.map(n => n.id));
    const connected = new Set(edges.flatMap(e => [e.source, e.target]));
    const disconnected = [...nodeIds].filter(id => !connected.has(id));
    if (disconnected.length > 0) {
      showError(`Validation failed: Disconnected nodes: ${disconnected.join(', ')}`);
    } else {
      showSuccess('Workflow is valid!');
    }
  };
  const handleRun = () => {
    try {
      // Placeholder: simulate execution
      showInfo('Simulating workflow execution...');
      // TODO: Integrate with backend
    } catch (err) {
      showError('Failed to run workflow.');
    }
  };
  const handleZoomIn = () => canvasRef.current?.zoomIn();
  const handleZoomOut = () => canvasRef.current?.zoomOut();
  const handleUndo = () => canvasRef.current?.undo();
  const handleRedo = () => canvasRef.current?.redo();

  // Helper: add a sample node
  const handleAddSampleNode = () => {
    if (canvasRef.current) {
      const id = `sample-${Date.now()}`;
      canvasRef.current.updateNodeLabel(id, 'New Node');
      // Actually add a node (simulate drag/drop)
      if (canvasRef.current.addNode) {
        canvasRef.current.addNode({
          id,
          type: 'default',
          position: { x: 200, y: 200 },
          data: { label: 'New Node' },
        });
      }
    }
  };

  const Toolbar = () => (
    <Paper sx={{ height: 64, p: 2, mb: 2, display: 'flex', alignItems: 'center' }}>
      <Stack direction="row" spacing={2}>
        <Button variant="contained" color="primary" startIcon={<SaveIcon />} onClick={handleSave}>Save</Button>
        <Button variant="outlined" color="primary" startIcon={<CheckCircleIcon />} onClick={handleValidate}>Validate</Button>
        <Button variant="contained" color="success" startIcon={<PlayArrowIcon />} onClick={handleRun}>Run</Button>
        <Button variant="outlined" startIcon={<ZoomInIcon />} onClick={handleZoomIn}>Zoom In</Button>
        <Button variant="outlined" startIcon={<ZoomOutIcon />} onClick={handleZoomOut}>Zoom Out</Button>
        <Button variant="outlined" startIcon={<UndoIcon />} onClick={handleUndo}>Undo</Button>
        <Button variant="outlined" startIcon={<RedoIcon />} onClick={handleRedo}>Redo</Button>
      </Stack>
    </Paper>
  );

  const PropertiesPanel: React.FC<{ node: Node | null; edge: Edge | null }> = ({ node, edge }) => {
    let error = '';
    if (node && !nodeLabel.trim()) error = 'Node label cannot be empty.';
    if (edge && !edgeLabel.trim()) error = 'Edge label cannot be empty.';
    return (
      <Paper sx={{ height: '100%', p: 2 }}>
        {node ? (
          <>
            <strong>Node Properties</strong>
            <TextField
              label="Label"
              value={nodeLabel}
              onChange={handleNodeLabelChange}
              fullWidth
              margin="normal"
              error={!!error}
              helperText={error}
            />
          </>
        ) : edge ? (
          <>
            <strong>Edge Properties</strong>
            <TextField
              label="Label"
              value={edgeLabel}
              onChange={handleEdgeLabelChange}
              fullWidth
              margin="normal"
              error={!!error}
              helperText={error}
            />
          </>
        ) : (
          <span>Select a node or edge to edit its properties.</span>
        )}
      </Paper>
    );
  };

  return (
    <Box sx={{ height: '100vh', background: theme.palette.background.default, p: { xs: 1, md: 0 } }}>
      <Grid container spacing={2} sx={{ height: '100%' }}>
        {/* Palette */}
        <Grid item xs={12} md={2} sx={{ borderRight: { md: `1px solid ${theme.palette.divider}` }, minWidth: { md: 220 } }}>
          <Palette />
        </Grid>
        {/* Main Area */}
        <Grid item xs={12} md={7} sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* Onboarding tip */}
          <Alert severity="info" sx={{ mb: 2 }} role="region" aria-label="Onboarding Tip">
            Welcome to the Workflow Builder! Start by dragging components from the Palette or use the Add Node button. All actions are keyboard accessible.
          </Alert>
          {/* Global loading and error states */}
          {isLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 6 }} role="status" aria-busy="true">
              <CircularProgress size={40} />
              <Box sx={{ ml: 2 }}>Loading workflow...</Box>
            </Box>
          )}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} role="alert">{error}</Alert>
          )}
          {/* Toolbar */}
          <Toolbar />
          {/* Canvas and Properties */}
          {nodes.length === 0 ? (
            <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f5', borderRadius: 2 }} role="region" aria-label="Empty Workflow State">
              <Box sx={{ fontSize: 24, mb: 2, color: 'text.secondary' }}>No nodes yet</Box>
              <Button variant="contained" color="primary" onClick={handleAddSampleNode} aria-label="Add a Node">Add a Node</Button>
              <Box sx={{ mt: 2, color: 'text.secondary' }}>Drag from the Palette or use the button above to get started.</Box>
            </Box>
          ) : (
            <Canvas
              ref={canvasRef}
              onNodeSelect={setSelectedNode}
              onEdgeSelect={setSelectedEdge}
              onNodesUpdate={handleNodesUpdate}
              onEdgesUpdate={handleEdgesUpdate}
            />
          )}
        </Grid>
        {/* Properties Panel */}
        <Grid item xs={12} md={3} sx={{ borderLeft: { md: `1px solid ${theme.palette.divider}` }, height: '100%' }}>
          <PropertiesPanel node={selectedNode} edge={selectedEdge} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default WorkflowBuilderScreen; 