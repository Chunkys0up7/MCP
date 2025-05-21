import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Tooltip,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  Collapse,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import { designTokens } from '../../design-system/theme';

export interface MCPItem {
  id: string;
  name: string;
  type: 'llm' | 'notebook' | 'data';
  description: string;
  config?: Record<string, unknown>;
}

interface MCPLibraryProps {
  onAddMCP: (mcp: MCPItem) => void;
}

const MCPLibrary: React.FC<MCPLibraryProps> = ({ onAddMCP }) => {
  const [mcps, setMcps] = useState<MCPItem[]>([]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  useEffect(() => {
    // TODO: Replace with actual API call
    setMcps([
      {
        id: 'llm-1',
        name: 'GPT-4',
        type: 'llm',
        description: 'OpenAI GPT-4 model for advanced language tasks',
        config: {
          model: 'gpt-4',
          temperature: 0.7,
          maxTokens: 2000,
        },
      },
      {
        id: 'notebook-1',
        name: 'Data Analysis',
        type: 'notebook',
        description: 'Jupyter notebook for data analysis and visualization',
        config: {
          kernel: 'python3',
          timeout: 300,
        },
      },
      {
        id: 'data-1',
        name: 'CSV Loader',
        type: 'data',
        description: 'Load and process CSV files',
        config: {
          delimiter: ',',
          encoding: 'utf-8',
        },
      },
    ]);
  }, []);

  const getMcpTypeColor = (type: MCPItem['type']) => {
    switch (type) {
      case 'llm':
        return designTokens.colors.nodeTypes.llm;
      case 'notebook':
        return designTokens.colors.nodeTypes.notebook;
      case 'data':
        return designTokens.colors.nodeTypes.data;
      default:
        return '#666';
    }
  };

  const handleDragStart = (event: React.DragEvent, mcp: MCPItem) => {
    event.dataTransfer.setData('application/json', JSON.stringify(mcp));
    event.dataTransfer.effectAllowed = 'move';
  };

  const toggleExpand = (mcpId: string) => {
    setExpanded(prev => ({
      ...prev,
      [mcpId]: !prev[mcpId],
    }));
  };

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 2 }}>
      <Typography variant="h6" gutterBottom>
        MCP Library
      </Typography>
      <List>
        {mcps.map((mcp) => (
          <ListItem
            key={mcp.id}
            disablePadding
            sx={{ mb: 1 }}
          >
            <Paper
              sx={{
                width: '100%',
                border: '1px solid',
                borderColor: getMcpTypeColor(mcp.type),
                '&:hover': {
                  boxShadow: 2,
                },
              }}
              draggable
              onDragStart={(e) => handleDragStart(e, mcp)}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Typography variant="h6" sx={{ flex: 1 }}>
                    {mcp.name}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => toggleExpand(mcp.id)}
                  >
                    {expanded[mcp.id] ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                  <Tooltip title="Learn more">
                    <IconButton size="small">
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {mcp.description}
                </Typography>
                <Collapse in={expanded[mcp.id]} timeout="auto" unmountOnExit>
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Configuration:
                    </Typography>
                    <pre style={{ 
                      margin: 0,
                      padding: '8px',
                      backgroundColor: '#f5f5f5',
                      borderRadius: '4px',
                      fontSize: '12px',
                      overflow: 'auto'
                    }}>
                      {JSON.stringify(mcp.config, null, 2)}
                    </pre>
                  </Box>
                </Collapse>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={() => onAddMCP(mcp)}
                >
                  Add to Chain
                </Button>
              </CardActions>
            </Paper>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default MCPLibrary; 