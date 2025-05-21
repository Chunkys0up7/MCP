import React from 'react';
import { Handle, Position } from 'reactflow';
import type { NodeProps } from 'reactflow';
import { Box, Typography, Paper } from '@mui/material';
import { designTokens } from '../../../design-system/theme';

interface BaseNodeData {
  label: string;
  type: 'llm' | 'notebook' | 'data';
  status?: 'idle' | 'running' | 'success' | 'error';
}

const getNodeColor = (type: BaseNodeData['type'], status?: BaseNodeData['status']) => {
  if (status === 'running') return designTokens.colors.primary;
  if (status === 'success') return designTokens.colors.success;
  if (status === 'error') return designTokens.colors.error;

  switch (type) {
    case 'llm':
      return designTokens.colors.nodeTypes.llm;
    case 'notebook':
      return designTokens.colors.nodeTypes.notebook;
    case 'data':
      return designTokens.colors.nodeTypes.data;
    default:
      return '#eee';
  }
};

const getStatusDescription = (status?: BaseNodeData['status']) => {
  switch (status) {
    case 'running':
      return 'Node is currently running';
    case 'success':
      return 'Node execution completed successfully';
    case 'error':
      return 'Node execution failed';
    default:
      return 'Node is idle';
  }
};

const BaseNode: React.FC<NodeProps<BaseNodeData>> = ({ data, selected }) => {
  const nodeColor = getNodeColor(data.type, data.status);
  const statusDescription = getStatusDescription(data.status);

  return (
    <Paper
      elevation={selected ? 4 : 1}
      sx={{
        width: 200,
        p: 2,
        bgcolor: nodeColor,
        color: 'white',
        borderRadius: 2,
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 3,
        },
        position: 'relative',
        overflow: 'visible',
      }}
      role="article"
      aria-label={`${data.label} node`}
      aria-describedby={`node-status-${data.label}`}
      tabIndex={0}
    >
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Top}
        style={{
          width: 12,
          height: 12,
          background: 'white',
          border: `2px solid ${nodeColor}`,
          borderRadius: '50%',
        }}
        aria-label="Input connection point"
      />

      {/* Node Content */}
      <Box sx={{ textAlign: 'center' }}>
        <Typography
          variant="subtitle2"
          sx={{
            fontFamily: '"IBM Plex Sans", sans-serif',
            fontWeight: 600,
            fontSize: '0.875rem',
            mb: 0.5,
          }}
        >
          {data.label}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            opacity: 0.8,
            fontSize: '0.75rem',
            textTransform: 'uppercase',
          }}
        >
          {data.type}
        </Typography>
      </Box>

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          width: 12,
          height: 12,
          background: 'white',
          border: `2px solid ${nodeColor}`,
          borderRadius: '50%',
        }}
        aria-label="Output connection point"
      />

      {/* Status Indicator */}
      {data.status && (
        <Box
          id={`node-status-${data.label}`}
          sx={{
            position: 'absolute',
            top: -4,
            right: -4,
            width: 16,
            height: 16,
            borderRadius: '50%',
            bgcolor: 'white',
            border: `2px solid ${nodeColor}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          role="status"
          aria-label={statusDescription}
        >
          {data.status === 'running' && (
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: nodeColor,
                animation: 'pulse 1.5s infinite',
                '@keyframes pulse': {
                  '0%': {
                    transform: 'scale(0.8)',
                    opacity: 0.5,
                  },
                  '50%': {
                    transform: 'scale(1.2)',
                    opacity: 1,
                  },
                  '100%': {
                    transform: 'scale(0.8)',
                    opacity: 0.5,
                  },
                },
              }}
            />
          )}
          {data.status === 'success' && (
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: designTokens.colors.success,
              }}
            />
          )}
          {data.status === 'error' && (
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: designTokens.colors.error,
              }}
            />
          )}
        </Box>
      )}
    </Paper>
  );
};

export default BaseNode; 