import React from 'react';
import { Box, Paper, Typography, CircularProgress, LinearProgress, Chip } from '@mui/material';
import { useWebSocket } from '../../../application/hooks/useWebSocket';
import { useWorkflowStore } from '../../../application/stores/workflowStore';
import { Node } from 'reactflow';

interface ExecutionStatusProps {
  workflowId: string;
}

export const ExecutionStatus: React.FC<ExecutionStatusProps> = ({ workflowId }) => {
  const { nodes } = useWorkflowStore();
  const { isConnected, getNodeStatus, getLatestResourceUpdate, errors } = useWebSocket(workflowId);
  const resourceUpdate = getLatestResourceUpdate();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'primary';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CircularProgress size={16} />;
      case 'completed':
        return '✓';
      case 'failed':
        return '✕';
      default:
        return '○';
    }
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Execution Status</Typography>
        <Chip
          label={isConnected ? 'Connected' : 'Disconnected'}
          color={isConnected ? 'success' : 'error'}
          size="small"
        />
      </Box>

      {resourceUpdate && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Resource Usage
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption">CPU</Typography>
              <LinearProgress
                variant="determinate"
                value={resourceUpdate.cpu}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption">Memory</Typography>
              <LinearProgress
                variant="determinate"
                value={resourceUpdate.memory}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </Box>
        </Box>
      )}

      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Node Status
        </Typography>
        {nodes.map((node: Node) => {
          const status = getNodeStatus(node.id);
          return (
            <Box
              key={node.id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mb: 1,
                p: 1,
                borderRadius: 1,
                bgcolor: 'background.default',
              }}
            >
              <Box sx={{ width: 24, height: 24, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {status ? getStatusIcon(status.status) : '○'}
              </Box>
              <Typography variant="body2" sx={{ flex: 1 }}>
                {node.data.label}
              </Typography>
              {status && (
                <Chip
                  label={status.status}
                  color={getStatusColor(status.status)}
                  size="small"
                />
              )}
              {status?.progress !== undefined && (
                <Box sx={{ width: 100 }}>
                  <LinearProgress
                    variant="determinate"
                    value={status.progress}
                    sx={{ height: 4, borderRadius: 2 }}
                  />
                </Box>
              )}
            </Box>
          );
        })}
      </Box>

      {errors.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" color="error" gutterBottom>
            Errors
          </Typography>
          {errors.map((error, index) => (
            <Typography key={index} variant="caption" color="error" display="block">
              {error}
            </Typography>
          ))}
        </Box>
      )}
    </Paper>
  );
}; 