import React from 'react';
import { Handle, Position } from 'reactflow';
import { Box, Typography } from '@mui/material';
import type { NodeProps } from 'reactflow';
import type { NodeData } from '../../../../infrastructure/types/node';

const NotebookNode: React.FC<NodeProps<NodeData>> = ({ data }) => {
  return (
    <Box
      sx={{
        padding: 2,
        borderRadius: 1,
        backgroundColor: 'secondary.main',
        color: 'secondary.contrastText',
        minWidth: 150,
        border: '1px solid',
        borderColor: 'secondary.dark',
      }}
    >
      <Handle type="target" position={Position.Left} />
      <Typography variant="subtitle1" gutterBottom>
        {data.label}
      </Typography>
      <Typography variant="body2" color="secondary.contrastText">
        Notebook Node
      </Typography>
      <Handle type="source" position={Position.Right} />
    </Box>
  );
};

export default NotebookNode; 