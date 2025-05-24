import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  CircularProgress,
  Collapse,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
} from '@mui/icons-material';
import { useWorkflowStore } from '../../../infrastructure/state/workflowStore';
import { workflowExecutionService, ExecutionState, ExecutionResult } from '../../../infrastructure/services/workflowExecutionService';

export const ExecutionPanel: React.FC = () => {
  const [expanded, setExpanded] = useState(true);
  const [executionState, setExecutionState] = useState<ExecutionState>(workflowExecutionService.getExecutionState());
  const { nodes, edges } = useWorkflowStore();

  useEffect(() => {
    const unsubscribe = workflowExecutionService.subscribe(setExecutionState);
    return () => unsubscribe();
  }, []);

  const handleExecute = async () => {
    try {
      await workflowExecutionService.executeWorkflow(nodes, edges);
    } catch (error) {
      console.error('Workflow execution failed:', error);
    }
  };

  const handleStop = () => {
    workflowExecutionService.stopExecution();
  };

  const getStatusIcon = (result: ExecutionResult) => {
    switch (result.status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'running':
        return <CircularProgress size={20} />;
      default:
        return <PendingIcon color="disabled" />;
    }
  };

  const getNodeLabel = (nodeId: string) => {
    const node = nodes.find(n => n.id === nodeId);
    return node?.data.label || nodeId;
  };

  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 16,
        left: 16,
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
          Execution Status
        </Typography>
        <IconButton
          onClick={handleExecute}
          disabled={executionState.isRunning}
          color="primary"
          size="small"
        >
          <PlayIcon />
        </IconButton>
        <IconButton
          onClick={handleStop}
          disabled={!executionState.isRunning}
          color="error"
          size="small"
        >
          <StopIcon />
        </IconButton>
        <IconButton onClick={() => setExpanded(!expanded)} size="small">
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      <Collapse in={expanded}>
        <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
          {Object.entries(executionState.results).map(([nodeId, result]) => (
            <ListItem key={nodeId}>
              <ListItemIcon>{getStatusIcon(result)}</ListItemIcon>
              <ListItemText
                primary={getNodeLabel(nodeId)}
                secondary={
                  result.status === 'error'
                    ? result.error
                    : result.status === 'success'
                    ? 'Completed successfully'
                    : result.status === 'running'
                    ? 'Running...'
                    : 'Pending'
                }
              />
            </ListItem>
          ))}
        </List>
      </Collapse>
    </Box>
  );
}; 