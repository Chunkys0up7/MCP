import React from 'react';
import { Node } from 'reactflow';
import {
  Box,
  Typography,
  TextField,
  Button,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';

interface MCPNodeData {
  label: string;
  type: 'llm' | 'notebook' | 'script';
  description?: string;
  config?: Record<string, any>;
}

interface PropertiesPanelProps {
  node: Node<MCPNodeData>;
}

export const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ node }) => {
  const { data } = node;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Node Properties
      </Typography>
      <Divider sx={{ mb: 2 }} />

      <TextField
        fullWidth
        label="Name"
        value={data.label}
        margin="normal"
        variant="outlined"
      />

      <FormControl fullWidth margin="normal">
        <InputLabel>Type</InputLabel>
        <Select value={data.type} label="Type">
          <MenuItem value="llm">LLM</MenuItem>
          <MenuItem value="notebook">Notebook</MenuItem>
          <MenuItem value="script">Script</MenuItem>
        </Select>
      </FormControl>

      <TextField
        fullWidth
        label="Description"
        value={data.description || ''}
        margin="normal"
        variant="outlined"
        multiline
        rows={3}
      />

      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Configuration
        </Typography>
        {data.type === 'llm' && (
          <>
            <TextField
              fullWidth
              label="Model"
              value={data.config?.model || ''}
              margin="normal"
              variant="outlined"
            />
            <TextField
              fullWidth
              label="Temperature"
              type="number"
              value={data.config?.temperature || 0.7}
              margin="normal"
              variant="outlined"
            />
          </>
        )}
        {data.type === 'notebook' && (
          <TextField
            fullWidth
            label="Notebook Path"
            value={data.config?.path || ''}
            margin="normal"
            variant="outlined"
          />
        )}
        {data.type === 'script' && (
          <TextField
            fullWidth
            label="Script Path"
            value={data.config?.path || ''}
            margin="normal"
            variant="outlined"
          />
        )}
      </Box>

      <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
        <Button variant="contained" color="primary" fullWidth>
          Save Changes
        </Button>
        <Button variant="outlined" color="error" fullWidth>
          Delete Node
        </Button>
      </Box>
    </Box>
  );
};

export default PropertiesPanel; 