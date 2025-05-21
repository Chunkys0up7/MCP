import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Slider,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import type { Node } from 'reactflow';

interface PropertiesPanelProps {
  selectedNode: Node | null;
  onUpdateNode: (nodeId: string, data: any) => void;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedNode,
  onUpdateNode,
}) => {
  if (!selectedNode) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body1" color="text.secondary">
          Select a node to view its properties
        </Typography>
      </Box>
    );
  }

  const handleConfigChange = (key: string, value: any) => {
    onUpdateNode(selectedNode.id, {
      config: {
        ...selectedNode.data.config,
        [key]: value,
      },
    });
  };

  const renderConfigFields = () => {
    switch (selectedNode.type) {
      case 'mcp':
        return (
          <>
            <FormControl fullWidth margin="normal">
              <InputLabel>Model</InputLabel>
              <Select
                value={selectedNode.data.config?.model || ''}
                label="Model"
                onChange={(e) => handleConfigChange('model', e.target.value)}
              >
                <MenuItem value="gpt-4">GPT-4</MenuItem>
                <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                <MenuItem value="claude-2">Claude 2</MenuItem>
              </Select>
            </FormControl>
            <Box sx={{ mt: 2 }}>
              <Typography gutterBottom>Temperature</Typography>
              <Slider
                value={selectedNode.data.config?.temperature || 0.7}
                min={0}
                max={1}
                step={0.1}
                onChange={(_, value) => handleConfigChange('temperature', value)}
                valueLabelDisplay="auto"
              />
            </Box>
          </>
        );
      case 'notebook':
        return (
          <TextField
            fullWidth
            margin="normal"
            label="Notebook Path"
            value={selectedNode.data.config?.path || ''}
            onChange={(e) => handleConfigChange('path', e.target.value)}
          />
        );
      case 'data':
        return (
          <TextField
            fullWidth
            margin="normal"
            label="Data Source"
            value={selectedNode.data.config?.source || ''}
            onChange={(e) => handleConfigChange('source', e.target.value)}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Node Properties
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          {selectedNode.data.label}
        </Typography>
        {renderConfigFields()}
      </Paper>
    </Box>
  );
};

export default PropertiesPanel; 