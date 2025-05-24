import React, { useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { useWorkflowValidator } from './WorkflowValidator';
import { ValidationError } from './types';

export const ValidationPanel: React.FC = () => {
  const [expanded, setExpanded] = useState(true);
  const { validateWorkflow } = useWorkflowValidator();
  const errors = validateWorkflow();

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  const getErrorIcon = (type: ValidationError['type']) => {
    switch (type) {
      case 'node':
        return <ErrorIcon color="error" />;
      case 'edge':
        return <ErrorIcon color="warning" />;
      case 'workflow':
        return <ErrorIcon color="error" />;
      default:
        return <ErrorIcon />;
    }
  };

  const groupedErrors = errors.reduce((acc, error) => {
    if (!acc[error.type]) {
      acc[error.type] = [];
    }
    acc[error.type].push(error);
    return acc;
  }, {} as Record<ValidationError['type'], ValidationError[]>);

  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 16,
        right: 16,
        width: 300,
        bgcolor: 'background.paper',
        borderRadius: 1,
        boxShadow: 3,
        zIndex: 1000,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          p: 1,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Typography variant="subtitle1" sx={{ flex: 1 }}>
          Validation Errors ({errors.length})
        </Typography>
        <IconButton onClick={handleToggle} size="small">
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      <Collapse in={expanded}>
        <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
          {Object.entries(groupedErrors).map(([type, typeErrors]) => (
            <React.Fragment key={type}>
              <ListItem>
                <ListItemText
                  primary={
                    <Typography variant="subtitle2" color="text.secondary">
                      {type.charAt(0).toUpperCase() + type.slice(1)} Errors
                    </Typography>
                  }
                />
              </ListItem>
              {typeErrors.map((error) => (
                <ListItem key={error.id || error.message}>
                  <ListItemIcon>{getErrorIcon(error.type)}</ListItemIcon>
                  <ListItemText
                    primary={error.message}
                    secondary={error.id ? `ID: ${error.id}` : undefined}
                  />
                </ListItem>
              ))}
            </React.Fragment>
          ))}
        </List>
      </Collapse>
    </Box>
  );
}; 