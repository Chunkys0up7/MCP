import React from 'react';
import { Handle, Position } from 'reactflow';
import { Box, Typography, IconButton, Tooltip, Paper } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import SettingsIcon from '@mui/icons-material/Settings';
import { useChainStore } from '../../../infrastructure/state/chainStore';
import { designTokens } from '../../design-system/theme';
import type { NodeData } from '../../../infrastructure/types/node';
import type { NodeProps } from 'reactflow';

type MCPNodeProps = NodeProps<NodeData>;

const MCPNode: React.FC<MCPNodeProps> = ({ data, selected, id }) => {
  const { removeNode, updateNode } = useChainStore();

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'llm':
        return '#2196f3';
      case 'notebook':
        return '#4caf50';
      case 'data':
        return '#ff9800';
      default:
        return '#757575';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return '#2196f3';
      case 'success':
        return '#4caf50';
      case 'error':
        return '#f44336';
      default:
        return '#757575';
    }
  };

  const handleDelete = (event: React.MouseEvent) => {
    event.stopPropagation();
    removeNode(id);
  };

  const handleConfigure = (event: React.MouseEvent) => {
    event.stopPropagation();
    // TODO: Open configuration dialog
  };

  return (
    <Paper
      elevation={selected ? 8 : 2}
      sx={{
        padding: 2,
        minWidth: 200,
        border: '2px solid',
        borderColor: getNodeColor(data.type),
        backgroundColor: 'background.paper',
        '&:hover': {
          boxShadow: 6,
        },
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: '#555',
          width: 8,
          height: 8,
        }}
      />
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography
          variant="subtitle1"
          sx={{
            flex: 1,
            fontWeight: 'bold',
            color: getNodeColor(data.type),
          }}
        >
          {data.label}
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title="Configure">
            <IconButton
              size="small"
              onClick={handleConfigure}
              sx={{ color: 'text.secondary' }}
            >
              <SettingsIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton
              size="small"
              onClick={handleDelete}
              sx={{ color: 'error.main' }}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          mt: 1,
        }}
      >
        <Box
          sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: getStatusColor(data.status),
          }}
        />
        <Typography variant="body2" color="text.secondary">
          {data.status}
        </Typography>
      </Box>
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: '#555',
          width: 8,
          height: 8,
        }}
      />
    </Paper>
  );
};

export default MCPNode; 