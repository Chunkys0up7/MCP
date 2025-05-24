import React from 'react';
import { Box, Typography } from '@mui/material';
import type { NodeProps } from 'reactflow';
import { MCPNode, MCPNodeProps } from './MCPNode';

interface OutputNodeData {
  label: string;
  type: string;
  onDelete?: (id: string) => void;
  onConfigure?: (id: string) => void;
}

export const OutputNode: React.FC<NodeProps<OutputNodeData>> = (props) => {
  const { data, id, ...rest } = props;
  
  return (
    <MCPNode
      data={{
        ...data,
        type: 'output',
      }}
      id={id}
      {...rest}
    >
      <Box sx={{ mt: 1 }}>
        <Typography variant="caption" display="block">
          Output Node
        </Typography>
      </Box>
    </MCPNode>
  );
}; 