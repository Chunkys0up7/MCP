import React, { ReactNode } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Box, Typography, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import SettingsIcon from '@mui/icons-material/Settings';

interface MCPNodeData {
  label: string;
  type: string;
  onDelete?: (id: string) => void;
  onConfigure?: (id: string) => void;
}

export interface MCPNodeProps extends NodeProps<MCPNodeData> {
  children?: ReactNode;
}

export const MCPNode: React.FC<MCPNodeProps> = ({ data, id, selected, type, zIndex, isConnectable, xPos, yPos, dragging, ...rest }) => {
  const getNodeColor = (type: string) => {
    switch (type) {
      case 'llm':
        return '#0b79ee';
      case 'notebook':
        return '#00bcd4';
      case 'data':
        return '#4caf50';
      case 'input':
        return '#ff9800';
      case 'output':
        return '#9c27b0';
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
        padding: 2,
        borderRadius: 1,
        backgroundColor: 'white',
        border: `2px solid ${getNodeColor(data.type)}`,
        minWidth: 150,
      }}
    >
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} />
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="subtitle2" sx={{ color: getNodeColor(data.type) }}>
          {data.type.toUpperCase()}
        </Typography>
        <Box>
          <IconButton size="small" onClick={handleConfigure}>
            <SettingsIcon fontSize="small" />
          </IconButton>
          <IconButton size="small" onClick={handleDelete}>
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>
      <Typography variant="body2">{data.label}</Typography>
      {rest.children}
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} />
    </Box>
  );
}; 