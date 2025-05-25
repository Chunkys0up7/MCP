import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useWorkflowValidation } from '../../../application/hooks/useWorkflowValidation';
import { useWorkflowStore } from '../../../infrastructure/state/workflowStore';
import { ValidationError } from '../../../domain/models/workflow';

export const ValidationPanel: React.FC = () => {
  const { nodes, edges } = useWorkflowStore();
  const {
    validationResult,
    validateWorkflow,
    isValid
  } = useWorkflowValidation(nodes, edges);

  const [expanded, setExpanded] = React.useState(true);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const getSeverityIcon = (severity: ValidationError['severity']) => {
    switch (severity) {
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return null;
    }
  };

  const getSeverityColor = (severity: ValidationError['severity']) => {
    switch (severity) {
      case 'error':
        return 'error.main';
      case 'warning':
        return 'warning.main';
      case 'info':
        return 'info.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <Paper
      elevation={2}
      sx={{
        position: 'absolute',
        bottom: 16,
        right: 16,
        width: 400,
        maxHeight: 400,
        overflow: 'auto',
        zIndex: 1000
      }}
    >
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: 1,
          borderColor: 'divider'
        }}
      >
        <Typography variant="h6">
          Validation Results
          {isValid && (
            <Typography
              component="span"
              variant="body2"
              color="success.main"
              sx={{ ml: 1 }}
            >
              (Valid)
            </Typography>
          )}
        </Typography>
        <Box>
          <Tooltip title="Refresh">
            <IconButton onClick={() => validateWorkflow()} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <IconButton onClick={handleExpandClick} size="small">
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
      </Box>

      <Collapse in={expanded}>
        <List dense>
          {validationResult.errors.map((error, index) => (
            <ListItem
              key={`error-${index}`}
              sx={{
                borderLeft: 4,
                borderColor: getSeverityColor(error.severity)
              }}
            >
              <ListItemIcon>
                {getSeverityIcon(error.severity)}
              </ListItemIcon>
              <ListItemText
                primary={error.message}
                secondary={
                  <>
                    <Typography
                      component="span"
                      variant="body2"
                      color="text.secondary"
                    >
                      Node: {error.nodeId}
                    </Typography>
                    {error.details && (
                      <Typography
                        component="div"
                        variant="caption"
                        color="text.secondary"
                        sx={{ mt: 0.5 }}
                      >
                        {error.details}
                      </Typography>
                    )}
                  </>
                }
              />
            </ListItem>
          ))}

          {validationResult.warnings.map((warning, index) => (
            <ListItem
              key={`warning-${index}`}
              sx={{
                borderLeft: 4,
                borderColor: getSeverityColor(warning.severity)
              }}
            >
              <ListItemIcon>
                {getSeverityIcon(warning.severity)}
              </ListItemIcon>
              <ListItemText
                primary={warning.message}
                secondary={
                  <>
                    <Typography
                      component="span"
                      variant="body2"
                      color="text.secondary"
                    >
                      Node: {warning.nodeId}
                    </Typography>
                    {warning.details && (
                      <Typography
                        component="div"
                        variant="caption"
                        color="text.secondary"
                        sx={{ mt: 0.5 }}
                      >
                        {warning.details}
                      </Typography>
                    )}
                  </>
                }
              />
            </ListItem>
          ))}

          {validationResult.errors.length === 0 && validationResult.warnings.length === 0 && (
            <ListItem>
              <ListItemText
                primary="No validation issues found"
                sx={{ color: 'success.main' }}
              />
            </ListItem>
          )}
        </List>
      </Collapse>
    </Paper>
  );
}; 