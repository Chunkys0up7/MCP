import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import type { NodeProps } from 'reactflow';
import { MCPNode } from './MCPNode';

interface DataNodeData {
  label: string;
  dataType: string;
  source: string;
  format: string;
  onDelete?: (id: string) => void;
  onConfigure?: (id: string) => void;
}

export const DataNode: React.FC<NodeProps<DataNodeData>> = (props) => {
  const { data, id, ...rest } = props;
  
  return (
    <MCPNode
      data={{
        ...data,
        type: 'data',
      }}
      id={id}
      {...rest}
    >
      <Box sx={{ mt: 1 }}>
        <Chip
          label={data.dataType}
          size="small"
          sx={{ mr: 1, mb: 1 }}
        />
        <Typography variant="caption" display="block">
          Source: {data.source}
        </Typography>
        <Typography variant="caption" display="block">
          Format: {data.format}
        </Typography>
      </Box>
    </MCPNode>
  );
}; 