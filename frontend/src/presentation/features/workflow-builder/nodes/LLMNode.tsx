import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import type { NodeProps } from 'reactflow';
import { MCPNode } from './MCPNode';

interface LLMNodeData {
  label: string;
  model: string;
  temperature: number;
  maxTokens: number;
  onDelete?: (id: string) => void;
  onConfigure?: (id: string) => void;
}

export const LLMNode: React.FC<NodeProps<LLMNodeData>> = ({ data, id }) => {
  return (
    <MCPNode
      data={{
        ...data,
        type: 'llm',
      }}
      id={id}
    >
      <Box sx={{ mt: 1 }}>
        <Chip
          label={data.model}
          size="small"
          sx={{ mr: 1, mb: 1 }}
        />
        <Typography variant="caption" display="block">
          Temperature: {data.temperature}
        </Typography>
        <Typography variant="caption" display="block">
          Max Tokens: {data.maxTokens}
        </Typography>
      </Box>
    </MCPNode>
  );
}; 