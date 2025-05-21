import React from 'react';
import { Handle, Position } from 'reactflow';
import { Box, Typography } from '@mui/material';
import type { NodeProps } from 'reactflow';
import type { NodeData } from '../../../../infrastructure/types/node';

const LLMNode: React.FC<NodeProps<NodeData>> = ({ data }) => {
  return (
    <Box
      sx={{
        padding: 2,
        borderRadius: 1,
        backgroundColor: 'primary.main',
        color: 'primary.contrastText',
        minWidth: 150,
        border: '1px solid',
        borderColor: 'primary.dark',
      }}
    >
      <Handle type="target" position={Position.Left} />
      <Typography variant="subtitle1" gutterBottom>
        {data.label}
      </Typography>
      <Typography variant="body2" color="primary.contrastText">
        LLM Node
      </Typography>
      <Handle type="source" position={Position.Right} />
    </Box>
  );
};

export default LLMNode; 