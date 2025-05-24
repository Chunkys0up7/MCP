import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
} from '@mui/material';
import {
  SmartToy as LLMIcon,
  Code as NotebookIcon,
  Storage as DataIcon,
} from '@mui/icons-material';
import { useWorkflowStore } from '../../../infrastructure/state/workflowStore';

interface NodeType {
  type: string;
  label: string;
  icon: React.ReactNode;
  defaultData: Record<string, any>;
}

const nodeTypes: NodeType[] = [
  {
    type: 'llm',
    label: 'LLM Node',
    icon: <LLMIcon />,
    defaultData: {
      label: 'LLM Node',
      type: 'llm',
      model: 'gpt-4',
      temperature: 0.7,
      maxTokens: 1000,
    },
  },
  {
    type: 'notebook',
    label: 'Notebook Node',
    icon: <NotebookIcon />,
    defaultData: {
      label: 'Notebook Node',
      type: 'notebook',
      notebookPath: '',
      kernel: 'python3',
      timeout: 300,
    },
  },
  {
    type: 'data',
    label: 'Data Node',
    icon: <DataIcon />,
    defaultData: {
      label: 'Data Node',
      type: 'data',
      dataType: 'csv',
      source: '',
      format: 'file',
    },
  },
];

export const NodePalette: React.FC = () => {
  const handleDragStart = (event: React.DragEvent, nodeType: NodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType.type);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <Paper
      sx={{
        width: 250,
        height: '100%',
        borderRight: 1,
        borderColor: 'divider',
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Node Palette
        </Typography>
        <List>
          {nodeTypes.map((nodeType) => (
            <ListItem
              key={nodeType.type}
              button
              draggable
              onDragStart={(e) => handleDragStart(e, nodeType)}
              sx={{
                mb: 1,
                borderRadius: 1,
                '&:hover': {
                  bgcolor: 'action.hover',
                },
              }}
            >
              <ListItemIcon>{nodeType.icon}</ListItemIcon>
              <ListItemText primary={nodeType.label} />
            </ListItem>
          ))}
        </List>
      </Box>
    </Paper>
  );
}; 