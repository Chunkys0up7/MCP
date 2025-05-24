import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import type { NodeProps } from 'reactflow';
import { MCPNode } from './MCPNode';

interface NotebookNodeData {
  label: string;
  notebookPath: string;
  kernel: string;
  timeout: number;
  onDelete?: (id: string) => void;
  onConfigure?: (id: string) => void;
}

export const NotebookNode: React.FC<NodeProps<NotebookNodeData>> = (props) => {
  const { data, id, ...rest } = props;
  
  return (
    <MCPNode
      data={{
        ...data,
        type: 'notebook',
      }}
      id={id}
      {...rest}
    >
      <Box sx={{ mt: 1 }}>
        <Chip
          label={data.kernel}
          size="small"
          sx={{ mr: 1, mb: 1 }}
        />
        <Typography variant="caption" display="block" sx={{ wordBreak: 'break-all' }}>
          Path: {data.notebookPath}
        </Typography>
        <Typography variant="caption" display="block">
          Timeout: {data.timeout}s
        </Typography>
      </Box>
    </MCPNode>
  );
}; 