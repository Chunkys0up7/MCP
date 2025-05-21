import React from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  IconButton,
  Tooltip,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { useChainStore } from '../../../infrastructure/state/chainStore';

interface InputVariable {
  name: string;
  description: string;
  type: string;
  required: boolean;
}

interface InputConfigProps {
  nodeId: string;
  inputVariables: InputVariable[];
}

const InputConfig: React.FC<InputConfigProps> = ({ nodeId, inputVariables }) => {
  const { nodes, updateNode } = useChainStore();

  const node = nodes.find((n) => n.id === nodeId);
  const inputValues = node?.data?.inputValues || {};

  const handleInputChange = (variableName: string, value: string) => {
    updateNode(nodeId, {
      data: {
        ...node?.data,
        inputValues: {
          ...inputValues,
          [variableName]: value,
        },
      },
    });
  };

  if (!inputVariables.length) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary">
          No input variables configured for this node.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Input Configuration
      </Typography>
      {inputVariables.map((variable) => (
        <Accordion
          key={variable.name}
          defaultExpanded
          sx={{
            '&:before': {
              display: 'none',
            },
            boxShadow: 'none',
            border: 1,
            borderColor: 'divider',
            mb: 1,
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            sx={{
              bgcolor: 'background.paper',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
              <Typography variant="subtitle1" sx={{ flex: 1 }}>
                {variable.name}
                {variable.required && (
                  <Typography
                    component="span"
                    color="error"
                    sx={{ ml: 0.5 }}
                  >
                    *
                  </Typography>
                )}
              </Typography>
              <Tooltip title={variable.description}>
                <IconButton size="small">
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <TextField
              fullWidth
              label="Value"
              value={inputValues[variable.name] || ''}
              onChange={(e) => handleInputChange(variable.name, e.target.value)}
              required={variable.required}
              error={variable.required && !inputValues[variable.name]}
              helperText={
                variable.required && !inputValues[variable.name]
                  ? 'This field is required'
                  : `Type: ${variable.type}`
              }
              inputProps={{
                'aria-label': `Input value for ${variable.name}`,
                'aria-required': variable.required ? 'true' : 'false',
              }}
            />
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

export default InputConfig; 