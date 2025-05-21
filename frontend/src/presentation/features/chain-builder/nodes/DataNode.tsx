import React from 'react';
import { Handle, Position } from 'reactflow';
import { Box, Typography } from '@mui/material';
import type { NodeProps } from 'reactflow';
import type { NodeData } from '../../../../infrastructure/types/node';

const DataNode: React.FC<NodeProps<NodeData>> = ({ data }) => {
  return (
    <Box
      sx={{
        padding: 2,
        borderRadius: 1,
        backgroundColor: 'info.main',
        color: 'info.contrastText',
        minWidth: 150,
        border: '1px solid',
        borderColor: 'info.dark',
      }}
    >
      <Handle type="target" position={Position.Left} />
      <Typography variant="subtitle1" gutterBottom>
        {data.label}
      </Typography>
      <Typography variant="body2" color="info.contrastText">
        Data Node
      </Typography>
      <Handle type="source" position={Position.Right} />
    </Box>
  );
};

export default DataNode; 