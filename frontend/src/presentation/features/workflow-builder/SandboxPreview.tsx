import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  CircularProgress,
  Alert,
  Grid,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Memory as CpuIcon,
} from '@mui/icons-material';
import { useSandbox } from '../../../application/hooks/useSandbox';
import { useWorkflowStore } from '../../../application/stores/workflowStore';
import { SandboxConfig } from '../../../infrastructure/services/sandboxService';

interface SandboxPreviewProps {
  workflowId: string;
}

export const SandboxPreview: React.FC<SandboxPreviewProps> = ({ workflowId }) => {
  const { nodes, edges } = useWorkflowStore();
  const {
    sandboxId,
    isLoading,
    error,
    metrics,
    createSandbox,
    executeInSandbox,
    runTests,
    validateInput,
    cleanup
  } = useSandbox(workflowId);

  const [input, setInput] = useState('');
  const [output, setOutput] = useState<any>(null);
  const [config, setConfig] = useState<SandboxConfig>({
    timeout: 30000,
    maxMemory: 512,
    maxCpu: 50,
    environment: 'development'
  });

  const handleCreateSandbox = useCallback(async () => {
    try {
      await createSandbox(config);
    } catch (err) {
      console.error('Failed to create sandbox:', err);
    }
  }, [createSandbox, config]);

  const handleExecute = useCallback(async () => {
    try {
      const result = await executeInSandbox(nodes, edges, JSON.parse(input));
      setOutput(result.output);
    } catch (err) {
      console.error('Failed to execute in sandbox:', err);
    }
  }, [executeInSandbox, nodes, edges, input]);

  const handleCleanup = useCallback(async () => {
    try {
      await cleanup();
      setOutput(null);
    } catch (err) {
      console.error('Failed to cleanup sandbox:', err);
    }
  }, [cleanup]);

  const formatMetric = (value: number, unit: string) => {
    return `${value.toFixed(2)} ${unit}`;
  };

  return (
    <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Sandbox Preview</Typography>
        <Box>
          {!sandboxId ? (
            <Button
              variant="contained"
              color="primary"
              onClick={handleCreateSandbox}
              disabled={isLoading}
              startIcon={isLoading ? <CircularProgress size={20} /> : <PlayIcon />}
            >
              Create Sandbox
            </Button>
          ) : (
            <Button
              variant="outlined"
              color="error"
              onClick={handleCleanup}
              disabled={isLoading}
              startIcon={<StopIcon />}
            >
              Cleanup
            </Button>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {metrics && (
        <Box sx={{ mb: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <SpeedIcon color="primary" />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Execution Time
                  </Typography>
                  <Typography variant="body2">
                    {formatMetric(metrics.executionTime, 'ms')}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <MemoryIcon color="primary" />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Memory Usage
                  </Typography>
                  <Typography variant="body2">
                    {formatMetric(metrics.memoryUsage, 'MB')}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CpuIcon color="primary" />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    CPU Usage
                  </Typography>
                  <Typography variant="body2">
                    {formatMetric(metrics.cpuUsage, '%')}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Box>
      )}

      <Grid container spacing={2} sx={{ flex: 1 }}>
        <Grid item xs={6}>
          <TextField
            label="Input"
            multiline
            rows={4}
            fullWidth
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!sandboxId || isLoading}
            placeholder="Enter JSON input..."
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            label="Output"
            multiline
            rows={4}
            fullWidth
            value={output ? JSON.stringify(output, null, 2) : ''}
            disabled
            placeholder="Output will appear here..."
          />
        </Grid>
      </Grid>

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleExecute}
          disabled={!sandboxId || isLoading}
          startIcon={isLoading ? <CircularProgress size={20} /> : <PlayIcon />}
        >
          Execute
        </Button>
        <Button
          variant="outlined"
          onClick={handleCleanup}
          disabled={!sandboxId || isLoading}
          startIcon={<RefreshIcon />}
        >
          Reset
        </Button>
      </Box>
    </Paper>
  );
}; 