import React from 'react';
import { Box, CssBaseline, ThemeProvider, Typography, Button, TextField } from '@mui/material';
import { SnackbarProvider, useSnackbar } from 'notistack';
import { theme } from './presentation/design-system/theme';
import WorkflowBuilder from './presentation/features/chain-builder/WorkflowBuilder';
import MCPLibrary from './presentation/features/chain-builder/MCPLibrary';
import PropertiesPanel from './presentation/features/chain-builder/PropertiesPanel';
import ExecutionConsole from './presentation/features/chain-builder/ExecutionConsole';
import { useFlowStore } from './store/flowStore';
import { initializeNotifier } from './services/notificationService';

// Component to initialize the notifier service
const NotifierInitializer: React.FC = () => {
  const { enqueueSnackbar } = useSnackbar();
  React.useEffect(() => {
    initializeNotifier(enqueueSnackbar);
  }, [enqueueSnackbar]);
  return null; // This component does not render anything
};

const App: React.FC = () => {
  const {
    nodes,
    edges,
    selectedNode,
    selectedEdge,
    setNodes,
    setEdges,
    setSelectedNode,
    setSelectedEdge,
    updateNodeData,
    updateEdgeLabel,
    loading,
    error,
    logs,
    loadWorkflowFromApi,
    saveWorkflowToApi,
    executeWorkflowFromApi,
  } = useFlowStore();

  // Workflow ID for demo/testing
  const [workflowId, setWorkflowId] = React.useState('demo');

  // Initialize with test nodes/edges on mount (only once)
  React.useEffect(() => {
    setNodes([
      {
        id: '1',
        type: 'input',
        position: { x: 250, y: 25 },
        data: { label: 'Input Node' },
      },
      {
        id: '2',
        type: 'default',
        position: { x: 100, y: 125 },
        data: { label: 'Default Node' },
      },
      {
        id: '3',
        type: 'output',
        position: { x: 250, y: 250 },
        data: { label: 'Output Node' },
      },
    ]);
    setEdges([
      { id: 'e1-2', source: '1', target: '2', label: '' },
      { id: 'e2-3', source: '2', target: '3', label: '' },
    ]);
    // eslint-disable-next-line
  }, []);

  const handleLabelChange = (label: string) => {
    if (selectedNode) updateNodeData(selectedNode.id, { label });
  };
  const handleDescriptionChange = (description: string) => {
    if (selectedNode) updateNodeData(selectedNode.id, { description });
  };
  const handleModelChange = (model: string) => {
    if (selectedNode) updateNodeData(selectedNode.id, { model });
  };
  const handlePathChange = (path: string) => {
    if (selectedNode) updateNodeData(selectedNode.id, { path });
  };
  const handleSourceChange = (source: string) => {
    if (selectedNode) updateNodeData(selectedNode.id, { source });
  };
  const handleEdgeLabelChange = (label: string) => {
    if (selectedEdge) updateEdgeLabel(selectedEdge.id, label);
  };

  // Map selectedNode/selectedEdge for PropertiesPanel
  const panelNode = selectedNode
    ? {
        id: selectedNode.id,
        type: selectedNode.type || '',
        data: {
          label: selectedNode.data.label,
          description: selectedNode.data.description,
          model: selectedNode.data.model,
          path: selectedNode.data.path,
          source: selectedNode.data.source,
        },
      }
    : null;
  const panelEdge = selectedEdge
    ? {
        id: selectedEdge.id,
        source: selectedEdge.source,
        target: selectedEdge.target,
        label: typeof selectedEdge.label === 'string' ? selectedEdge.label : '',
      }
    : null;

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <NotifierInitializer />
        <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ p: 2, backgroundColor: 'primary.main', color: 'white', display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h4" sx={{ flex: 1 }}>
              MCP Workflow Builder
            </Typography>
            <TextField
              size="small"
              label="Workflow ID"
              value={workflowId}
              onChange={e => setWorkflowId(e.target.value)}
              sx={{ bgcolor: 'white', borderRadius: 1, minWidth: 120 }}
            />
            <Button
              variant="contained"
              color="secondary"
              onClick={() => loadWorkflowFromApi(workflowId)}
              disabled={loading}
              sx={{ ml: 1 }}
            >
              Load
            </Button>
            <Button
              variant="contained"
              color="secondary"
              onClick={() => saveWorkflowToApi(workflowId)}
              disabled={loading}
              sx={{ ml: 1 }}
            >
              Save
            </Button>
            <Button
              variant="contained"
              color="success"
              onClick={() => executeWorkflowFromApi(workflowId)}
              disabled={loading}
              sx={{ ml: 1 }}
            >
              Execute
            </Button>
          </Box>
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'row', position: 'relative', minHeight: 0 }}>
            <MCPLibrary />
            <Box sx={{ flex: 1, position: 'relative' }}>
              <WorkflowBuilder />
            </Box>
            <PropertiesPanel
              selectedNode={panelNode}
              selectedEdge={panelEdge}
              onLabelChange={handleLabelChange}
              onDescriptionChange={handleDescriptionChange}
              onModelChange={handleModelChange}
              onPathChange={handlePathChange}
              onSourceChange={handleSourceChange}
              onEdgeLabelChange={handleEdgeLabelChange}
            />
          </Box>
          <ExecutionConsole loading={loading} error={error} logs={logs} />
        </Box>
      </SnackbarProvider>
    </ThemeProvider>
  );
};

export default App;
