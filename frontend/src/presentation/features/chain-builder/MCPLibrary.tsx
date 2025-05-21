import React from 'react';
import { Box, Typography, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider } from '@mui/material';
import StorageIcon from '@mui/icons-material/Storage';
import DescriptionIcon from '@mui/icons-material/Description';
import SmartToyIcon from '@mui/icons-material/SmartToy';

const MCP_TYPES = [
  {
    type: 'llm',
    label: 'LLM Node',
    icon: <SmartToyIcon sx={{ color: '#3B82F6' }} />,
    description: 'Large Language Model node',
    color: '#3B82F6',
  },
  {
    type: 'notebook',
    label: 'Notebook Node',
    icon: <DescriptionIcon sx={{ color: '#8B5CF6' }} />,
    description: 'Notebook execution node',
    color: '#8B5CF6',
  },
  {
    type: 'data',
    label: 'Data Node',
    icon: <StorageIcon sx={{ color: '#10B981' }} />,
    description: 'Data source node',
    color: '#10B981',
  },
];

const MCPLibrary: React.FC = () => {
  // Drag event handlers (stub for now)
  const handleDragStart = (event: React.DragEvent, type: string) => {
    event.dataTransfer.setData('application/reactflow', type);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <Box sx={{ width: 240, height: '100%', bgcolor: 'background.paper', borderRight: '1px solid #E5E7EB', p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        MCP Library
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <List>
        {MCP_TYPES.map((item) => (
          <ListItem key={item.type} disablePadding sx={{ mb: 1 }}>
            <ListItemButton
              draggable
              onDragStart={(e) => handleDragStart(e, item.type)}
              sx={{
                border: `2px solid ${item.color}`,
                borderRadius: 2,
                mb: 1,
                '&:hover': { backgroundColor: `${item.color}10` },
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText
                primary={<Typography sx={{ fontWeight: 500 }}>{item.label}</Typography>}
                secondary={<Typography variant="caption">{item.description}</Typography>}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default MCPLibrary; 