import React from 'react';
import {
  Box,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
} from '@mui/material';
import { Node } from 'reactflow';

interface PropertiesPanelProps {
  selectedNode: {
    id: string;
    type: string;
    data: { label: string; description?: string; model?: string; path?: string; source?: string };
  } | null;
  selectedEdge?: {
    id: string;
    source: string;
    target: string;
    label: string;
  } | null;
  onLabelChange?: (label: string) => void;
  onDescriptionChange?: (description: string) => void;
  onModelChange?: (model: string) => void;
  onPathChange?: (path: string) => void;
  onSourceChange?: (source: string) => void;
  onEdgeLabelChange?: (label: string) => void;
}

const LLM_MODELS = ['gpt-4', 'gpt-3.5-turbo', 'claude-2'];

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedNode,
  selectedEdge,
  onLabelChange,
  onDescriptionChange,
  onModelChange,
  onPathChange,
  onSourceChange,
  onEdgeLabelChange,
}) => {
  if (selectedEdge) {
    return (
      <Box sx={{ width: 280, height: '100%', bgcolor: 'background.paper', borderLeft: '1px solid #E5E7EB', p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
          Edge Properties
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Edge ID: {selectedEdge.id}
        </Typography>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Source: {selectedEdge.source}
        </Typography>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Target: {selectedEdge.target}
        </Typography>
        <TextField
          label="Label"
          value={selectedEdge.label}
          onChange={e => onEdgeLabelChange && onEdgeLabelChange(e.target.value)}
          fullWidth
          sx={{ mb: 2 }}
        />
      </Box>
    );
  }

  if (!selectedNode) {
    return (
      <Box sx={{ width: 280, height: '100%', bgcolor: 'background.paper', borderLeft: '1px solid #E5E7EB', p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
          Properties
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Typography variant="body2" color="text.secondary">
          Select a node or edge to view and edit its properties.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: 280, height: '100%', bgcolor: 'background.paper', borderLeft: '1px solid #E5E7EB', p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Properties
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <Typography variant="subtitle2" sx={{ mb: 1 }}>
        Node ID: {selectedNode.id}
      </Typography>
      <Typography variant="subtitle2" sx={{ mb: 1 }}>
        Type: {selectedNode.type}
      </Typography>
      <TextField
        label="Label"
        value={selectedNode.data.label}
        onChange={e => onLabelChange && onLabelChange(e.target.value)}
        fullWidth
        sx={{ mb: 2 }}
      />
      <TextField
        label="Description"
        value={selectedNode.data.description || ''}
        onChange={e => onDescriptionChange && onDescriptionChange(e.target.value)}
        fullWidth
        sx={{ mb: 2 }}
      />
      {selectedNode.type === 'llm' && (
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Model</InputLabel>
          <Select
            value={selectedNode.data.model || ''}
            label="Model"
            onChange={e => onModelChange && onModelChange(e.target.value)}
          >
            {LLM_MODELS.map((model) => (
              <MenuItem key={model} value={model}>{model}</MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
      {selectedNode.type === 'notebook' && (
        <TextField
          label="Notebook Path"
          value={selectedNode.data.path || ''}
          onChange={e => onPathChange && onPathChange(e.target.value)}
          fullWidth
          sx={{ mb: 2 }}
        />
      )}
      {selectedNode.type === 'data' && (
        <TextField
          label="Data Source"
          value={selectedNode.data.source || ''}
          onChange={e => onSourceChange && onSourceChange(e.target.value)}
          fullWidth
          sx={{ mb: 2 }}
        />
      )}
    </Box>
  );
};

export default PropertiesPanel; 