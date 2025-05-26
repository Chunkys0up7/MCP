import React from 'react';
import {
  Box,
  Typography,
  IconButton,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  SelectChangeEvent,
  Alert,
  AlertTitle
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { Node } from 'reactflow';
import { useWorkflowStore } from '../../../infrastructure/state/workflowStore';
import { useWorkflowValidation } from '../../../application/hooks/useWorkflowValidation';

interface NodeConfigPanelProps {
  node: Node;
  onClose: () => void;
}

export const NodeConfigPanel: React.FC<NodeConfigPanelProps> = ({
  node,
  onClose
}) => {
  const { updateNodeData, nodes, edges } = useWorkflowStore();
  const { getErrorsForNode, getWarningsForNode } = useWorkflowValidation(nodes, edges);

  const errors = getErrorsForNode(node.id);
  const warnings = getWarningsForNode(node.id);

  const handleLabelChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateNodeData(node.id, { label: event.target.value });
  };

  const handleTypeChange = (event: SelectChangeEvent<string>) => {
    updateNodeData(node.id, { type: event.target.value });
  };

  const handleTemperatureChange = (_: Event, value: number | number[]) => {
    updateNodeData(node.id, { temperature: value });
  };

  const handleMaxTokensChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateNodeData(node.id, { maxTokens: parseInt(event.target.value) });
  };

  const handleKernelChange = (event: SelectChangeEvent<string>) => {
    updateNodeData(node.id, { kernel: event.target.value });
  };

  const handleTimeoutChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateNodeData(node.id, { timeout: parseInt(event.target.value) });
  };

  const handleDataTypeChange = (event: SelectChangeEvent<string>) => {
    updateNodeData(node.id, { dataType: event.target.value });
  };

  const handleSourceChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateNodeData(node.id, { source: event.target.value });
  };

  const handleFormatChange = (event: SelectChangeEvent<string>) => {
    updateNodeData(node.id, { format: event.target.value });
  };

  const renderLLMConfig = () => (
    <>
      <TextField
        fullWidth
        label="Model"
        value={node.data.model || ''}
        onChange={(e) => updateNodeData(node.id, { model: e.target.value })}
        margin="normal"
      />
      <Typography gutterBottom>Temperature</Typography>
      <Slider
        value={node.data.temperature || 0.7}
        onChange={handleTemperatureChange}
        min={0}
        max={1}
        step={0.1}
        marks
        valueLabelDisplay="auto"
      />
      <TextField
        fullWidth
        label="Max Tokens"
        type="number"
        value={node.data.maxTokens || 1000}
        onChange={handleMaxTokensChange}
        margin="normal"
      />
    </>
  );

  const renderNotebookConfig = () => (
    <>
      <TextField
        fullWidth
        label="Notebook Path"
        value={node.data.notebookPath || ''}
        onChange={(e) => updateNodeData(node.id, { notebookPath: e.target.value })}
        margin="normal"
      />
      <FormControl fullWidth margin="normal">
        <InputLabel>Kernel</InputLabel>
        <Select<string>
          value={node.data.kernel || 'python3'}
          onChange={handleKernelChange}
          label="Kernel"
        >
          <MenuItem value="python3">Python 3</MenuItem>
          <MenuItem value="r">R</MenuItem>
          <MenuItem value="julia">Julia</MenuItem>
        </Select>
      </FormControl>
      <TextField
        fullWidth
        label="Timeout (seconds)"
        type="number"
        value={node.data.timeout || 300}
        onChange={handleTimeoutChange}
        margin="normal"
      />
    </>
  );

  const renderDataConfig = () => (
    <>
      <FormControl fullWidth margin="normal">
        <InputLabel>Data Type</InputLabel>
        <Select<string>
          value={node.data.dataType || 'csv'}
          onChange={handleDataTypeChange}
          label="Data Type"
        >
          <MenuItem value="csv">CSV</MenuItem>
          <MenuItem value="json">JSON</MenuItem>
          <MenuItem value="parquet">Parquet</MenuItem>
          <MenuItem value="excel">Excel</MenuItem>
        </Select>
      </FormControl>
      <TextField
        fullWidth
        label="Source"
        value={node.data.source || ''}
        onChange={handleSourceChange}
        margin="normal"
      />
      <FormControl fullWidth margin="normal">
        <InputLabel>Format</InputLabel>
        <Select<string>
          value={node.data.format || 'file'}
          onChange={handleFormatChange}
          label="Format"
        >
          <MenuItem value="file">File</MenuItem>
          <MenuItem value="url">URL</MenuItem>
          <MenuItem value="database">Database</MenuItem>
        </Select>
      </FormControl>
    </>
  );

  return (
    <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Node Configuration</Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      {(errors.length > 0 || warnings.length > 0) && (
        <Box sx={{ mb: 2 }}>
          {errors.map((error, index) => (
            <Alert severity="error" key={`error-${index}`} sx={{ mb: 1 }}>
              <AlertTitle>Error</AlertTitle>
              {error.message}
              {error.details && (
                <Typography variant="caption" component="div" sx={{ mt: 0.5 }}>
                  {typeof error.details === 'object' ? JSON.stringify(error.details) : error.details}
                </Typography>
              )}
            </Alert>
          ))}

          {warnings.map((warning, index) => (
            <Alert severity="warning" key={`warning-${index}`} sx={{ mb: 1 }}>
              <AlertTitle>Warning</AlertTitle>
              {warning.message}
              {warning.details && (
                <Typography variant="caption" component="div" sx={{ mt: 0.5 }}>
                  {typeof warning.details === 'object' ? JSON.stringify(warning.details) : warning.details}
                </Typography>
              )}
            </Alert>
          ))}
        </Box>
      )}

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <TextField
          fullWidth
          label="Label"
          value={node.data.label || ''}
          onChange={handleLabelChange}
          margin="normal"
        />
        <FormControl fullWidth margin="normal">
          <InputLabel>Type</InputLabel>
          <Select<string>
            value={node.data.type || 'mcp'}
            onChange={handleTypeChange}
            label="Type"
          >
            <MenuItem value="llm">LLM</MenuItem>
            <MenuItem value="notebook">Notebook</MenuItem>
            <MenuItem value="data">Data</MenuItem>
          </Select>
        </FormControl>
        {node.data.type === 'llm' && renderLLMConfig()}
        {node.data.type === 'notebook' && renderNotebookConfig()}
        {node.data.type === 'data' && renderDataConfig()}
      </Box>

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Button onClick={onClose}>Close</Button>
      </Box>
    </Box>
  );
}; 