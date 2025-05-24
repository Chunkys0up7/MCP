import React from 'react';
import { Box, Typography } from '@mui/material';
import type { NodeProps } from 'reactflow';
import { MCPNode, MCPNodeProps } from './MCPNode';

interface InputNodeData {
  label: string;
  type: string;
  onDelete?: (id: string) => void;
  onConfigure?: (id: string) => void;
}

export const InputNode: React.FC<NodeProps<InputNodeData>> = (props) => {
  const { data, id, ...rest } = props;
  
  return (
    <MCPNode
      data={{
        ...data,
        type: 'input',
      }}
      id={id}
      {...rest}
    >
      <Box sx={{ mt: 1 }}>
        <Typography variant="caption" display="block">
          Input Node
        </Typography>
      </Box>
    </MCPNode>
  );
}; 