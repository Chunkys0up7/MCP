import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Paper, Typography, Box } from '@mui/material';

interface MCPNodeData {
  label: string;
  type: 'llm' | 'notebook' | 'script';
  description?: string;
}

export const MCPNode = memo(({ data }: NodeProps<MCPNodeData>) => {
  const getNodeColor = (type: string) => {
    switch (type) {
      case 'llm':
        return '#2196f3'; // Blue
      case 'notebook':
        return '#4caf50'; // Green
      case 'script':
        return '#ff9800'; // Orange
      default:
        return '#9e9e9e'; // Grey
    }
  };

  return (
    <Paper
      sx={{
        padding: 2,
        minWidth: 200,
        backgroundColor: getNodeColor(data.type),
        color: 'white',
      }}
    >
      <Handle type="target" position={Position.Top} />
      <Box>
        <Typography variant="subtitle1" fontWeight="bold">
          {data.label}
        </Typography>
        <Typography variant="caption" display="block">
          {data.type.toUpperCase()}
        </Typography>
        {data.description && (
          <Typography variant="body2" sx={{ mt: 1 }}>
            {data.description}
          </Typography>
        )}
      </Box>
      <Handle type="source" position={Position.Bottom} />
    </Paper>
  );
}); 