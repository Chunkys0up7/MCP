import React from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText } from '@mui/material';
import { DragEvent } from 'react';

interface MCPTemplate {
  id: string;
  label: string;
  type: 'llm' | 'notebook' | 'script';
  description: string;
}

const mcpTemplates: MCPTemplate[] = [
  {
    id: 'llm-1',
    label: 'Claude Prompt',
    type: 'llm',
    description: 'Process text using Claude AI',
  },
  {
    id: 'notebook-1',
    label: 'Data Analysis',
    type: 'notebook',
    description: 'Analyze data using Python notebooks',
  },
  {
    id: 'script-1',
    label: 'Custom Script',
    type: 'script',
    description: 'Run custom Python scripts',
  },
];

interface MCPLibraryProps {
  onDragStart: (event: DragEvent, nodeType: string) => void;
}

export const MCPLibrary: React.FC<MCPLibraryProps> = ({ onDragStart }) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        MCP Library
      </Typography>
      <List>
        {mcpTemplates.map((template) => (
          <ListItem
            key={template.id}
            draggable
            onDragStart={(event) => onDragStart(event, template.id)}
            sx={{
              cursor: 'grab',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <Paper
              sx={{
                p: 1,
                width: '100%',
                backgroundColor: template.type === 'llm' ? '#2196f3' :
                  template.type === 'notebook' ? '#4caf50' : '#ff9800',
                color: 'white',
              }}
            >
              <ListItemText
                primary={template.label}
                secondary={template.description}
                primaryTypographyProps={{ fontWeight: 'bold' }}
                secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.7)' }}
              />
            </Paper>
          </ListItem>
        ))}
      </List>
    </Box>
  );
}; 