import React from 'react';
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
  Tooltip,
  Paper,
} from '@mui/material';
import type { Node } from 'reactflow';
import { useChainStore } from '../../../infrastructure/state/chainStore';
import InputConfig from '../chain-builder/InputConfig';
import type { NodeData, NodeConfig, NodeConfigData } from '../../../infrastructure/types/node';

interface PropertiesPanelProps {
  node: Node<NodeData>;
  onUpdate: (nodeId: string, data: Record<string, unknown>) => void;
}

const defaultConfig: NodeConfig = {
  llm: {
    model: 'gpt-4',
    temperature: 0.7,
    maxTokens: 1000,
    prompt: '',
  },
  notebook: {
    name: '',
    description: '',
    tags: [],
  },
  data: {
    source: '',
    format: 'json',
    schema: '',
  },
};

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ node, onUpdate }) => {
  const [config, setConfig] = React.useState<NodeConfig[keyof NodeConfig] | null>(null);

  React.useEffect(() => {
    if (node) {
      const nodeData = node.data as NodeConfigData;
      setConfig(nodeData.config || defaultConfig[nodeData.type]);
    }
  }, [node]);

  const handleConfigChange = (field: string, value: unknown) => {
    if (!node || !config) return;

    const newConfig = { ...config, [field]: value };
    setConfig(newConfig);
    onUpdate(node.id, { 
      ...node.data,
      config: newConfig 
    });
  };

  const handleDeleteNode = () => {
    if (!node) return;
    // TODO: Implement node deletion
  };

  if (!node) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Select a node to view its properties.
        </Typography>
      </Box>
    );
  }

  const nodeData = node.data as NodeConfigData;

  // Mock input variables for now - will be replaced with actual MCP configuration
  const inputVariables = [
    {
      name: 'prompt',
      description: 'The input prompt for the LLM',
      type: 'string',
      required: true,
    },
    {
      name: 'temperature',
      description: 'Controls randomness in the output',
      type: 'number',
      required: false,
    },
  ];

  const renderLLMConfig = () => {
    const llmConfig = config as NodeConfig['llm'];
    return (
      <>
        <FormControl fullWidth size="small" sx={{ mb: 2 }}>
          <InputLabel id="model-select-label">Model</InputLabel>
          <Select
            labelId="model-select-label"
            value={llmConfig.model}
            label="Model"
            onChange={(e) => handleConfigChange('model', e.target.value)}
            aria-describedby="model-select-helper"
          >
            <MenuItem value="gpt-4">GPT-4</MenuItem>
            <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
            <MenuItem value="claude-2">Claude 2</MenuItem>
          </Select>
          <Typography id="model-select-helper" variant="caption" color="text.secondary">
            Select the language model to use
          </Typography>
        </FormControl>

        <TextField
          fullWidth
          size="small"
          type="number"
          label="Temperature"
          value={llmConfig.temperature}
          onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
          inputProps={{ 
            min: 0, 
            max: 1, 
            step: 0.1,
            'aria-label': 'Temperature value between 0 and 1'
          }}
          helperText="Controls randomness in the output (0-1)"
          sx={{ mb: 2 }}
        />

        <TextField
          fullWidth
          size="small"
          type="number"
          label="Max Tokens"
          value={llmConfig.maxTokens}
          onChange={(e) => handleConfigChange('maxTokens', parseInt(e.target.value))}
          inputProps={{ 
            min: 1,
            'aria-label': 'Maximum number of tokens'
          }}
          helperText="Maximum length of the generated response"
          sx={{ mb: 2 }}
        />

        <TextField
          fullWidth
          multiline
          rows={4}
          label="Prompt"
          value={llmConfig.prompt}
          onChange={(e) => handleConfigChange('prompt', e.target.value)}
          helperText="Enter the prompt for the language model"
          inputProps={{
            'aria-label': 'Prompt text for the language model'
          }}
        />
      </>
    );
  };

  const renderNotebookConfig = () => {
    const notebookConfig = config as NodeConfig['notebook'];
    return (
      <>
        <TextField
          fullWidth
          size="small"
          label="Name"
          value={notebookConfig.name}
          onChange={(e) => handleConfigChange('name', e.target.value)}
          helperText="Name of the notebook"
          inputProps={{
            'aria-label': 'Notebook name'
          }}
          sx={{ mb: 2 }}
        />

        <TextField
          fullWidth
          multiline
          rows={2}
          label="Description"
          value={notebookConfig.description}
          onChange={(e) => handleConfigChange('description', e.target.value)}
          helperText="Description of the notebook's purpose"
          inputProps={{
            'aria-label': 'Notebook description'
          }}
          sx={{ mb: 2 }}
        />

        <TextField
          fullWidth
          size="small"
          label="Tags"
          value={notebookConfig.tags.join(', ')}
          onChange={(e) => handleConfigChange('tags', e.target.value.split(',').map(tag => tag.trim()))}
          helperText="Comma-separated tags for organization"
          inputProps={{
            'aria-label': 'Notebook tags'
          }}
        />
      </>
    );
  };

  const renderDataConfig = () => {
    const dataConfig = config as NodeConfig['data'];
    return (
      <>
        <TextField
          fullWidth
          size="small"
          label="Source"
          value={dataConfig.source}
          onChange={(e) => handleConfigChange('source', e.target.value)}
          helperText="Data source URL or path"
          inputProps={{
            'aria-label': 'Data source location'
          }}
          sx={{ mb: 2 }}
        />

        <FormControl fullWidth size="small" sx={{ mb: 2 }}>
          <InputLabel id="format-select-label">Format</InputLabel>
          <Select
            labelId="format-select-label"
            value={dataConfig.format}
            label="Format"
            onChange={(e) => handleConfigChange('format', e.target.value)}
            aria-describedby="format-select-helper"
          >
            <MenuItem value="json">JSON</MenuItem>
            <MenuItem value="csv">CSV</MenuItem>
            <MenuItem value="xml">XML</MenuItem>
          </Select>
          <Typography id="format-select-helper" variant="caption" color="text.secondary">
            Select the data format
          </Typography>
        </FormControl>

        <TextField
          fullWidth
          multiline
          rows={4}
          label="Schema"
          value={dataConfig.schema}
          onChange={(e) => handleConfigChange('schema', e.target.value)}
          helperText="JSON Schema or format specification"
          inputProps={{
            'aria-label': 'Data schema definition'
          }}
        />
      </>
    );
  };

  const renderConfig = () => {
    switch (nodeData.type) {
      case 'llm':
        return renderLLMConfig();
      case 'notebook':
        return renderNotebookConfig();
      case 'data':
        return renderDataConfig();
      default:
        return null;
    }
  };

  return (
    <Box sx={{ height: '100%', overflow: 'auto' }}>
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Node Properties
        </Typography>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1">ID: {node.id}</Typography>
          <Typography variant="subtitle1">Type: {node.data.type}</Typography>
          <Typography variant="subtitle1">Label: {node.data.label}</Typography>
          {node.data.config && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2">Configuration:</Typography>
              <pre style={{ margin: 0, padding: '8px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                {JSON.stringify(node.data.config, null, 2)}
              </pre>
            </Box>
          )}
        </Paper>
      </Box>
      <Divider />
      <Box sx={{ p: 2 }}>
        {renderConfig()}
      </Box>
      <Box sx={{ p: 2 }}>
        <InputConfig
          nodeId={node.id}
          inputVariables={inputVariables}
        />
      </Box>
      <Box sx={{ mt: 3, display: 'flex', gap: 1, p: 2 }}>
        <Tooltip title="Save changes to the node configuration">
          <Button 
            variant="contained" 
            color="primary" 
            fullWidth
            aria-label="Save changes"
          >
            Save Changes
          </Button>
        </Tooltip>
        <Tooltip title="Delete this node from the chain">
          <Button 
            variant="outlined" 
            color="error" 
            fullWidth
            onClick={handleDeleteNode}
            aria-label="Delete node"
          >
            Delete Node
          </Button>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default PropertiesPanel; 