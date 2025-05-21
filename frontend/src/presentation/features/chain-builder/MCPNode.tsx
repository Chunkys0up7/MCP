import React from 'react';
import { Handle, Position } from 'reactflow';
import { Box, Typography, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import SettingsIcon from '@mui/icons-material/Settings';
import type { NodeProps } from 'reactflow';
import type { NodeData } from '../../../infrastructure/types/node';

const MCPNode: React.FC<NodeProps<NodeData>> = ({ data, id }) => {
  const getNodeColor = (type: string) => {
    switch (type) {
      case 'llm':
        return '#0b79ee';
      case 'notebook':
        return '#00bcd4';
      case 'data':
        return '#4caf50';
      default:
        return '#314c68';
    }
  };

  const handleDelete = () => {
    if (data.onDelete) {
      data.onDelete(id);
    }
  };

  const handleConfigure = () => {
    if (data.onConfigure) {
      data.onConfigure(id);
    }
  };

  return (
    <Box
      sx={{
        width: 200,
        bgcolor: 'background.paper',
        border: 2,
        borderColor: getNodeColor(data.type),
        borderRadius: 2,
        p: 2,
        position: 'relative',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{
          width: 8,
          height: 8,
          background: '#314c68',
          border: '1px solid #ffffff',
        }}
      />
      
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="h3" sx={{ flex: 1, color: 'text.primary' }}>
          {data.label}
        </Typography>
        <IconButton
          size="small"
          onClick={handleConfigure}
          sx={{ color: 'text.secondary', '&:hover': { color: 'primary.main' } }}
        >
          <SettingsIcon fontSize="small" />
        </IconButton>
        <IconButton
          size="small"
          onClick={handleDelete}
          sx={{ color: 'text.secondary', '&:hover': { color: 'error.main' } }}
        >
          <DeleteIcon fontSize="small" />
        </IconButton>
      </Box>

      <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
        {data.type.toUpperCase()}
      </Typography>

      {data.description && (
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          {data.description}
        </Typography>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          width: 8,
          height: 8,
          background: '#314c68',
          border: '1px solid #ffffff',
        }}
      />
    </Box>
  );
};

export default MCPNode; 