import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, CircularProgress, IconButton, Tooltip } from '@mui/material';
import { PlayArrow, Stop, Refresh, Error as ErrorIcon, CheckCircle } from '@mui/icons-material';
import { useWorkflowExecution } from '../../../application/hooks/useWorkflowExecution';
import { WorkflowExecutionStatus } from '../../../domain/models/workflow';
import { ResourceUsagePanel } from './ResourceUsagePanel';
import { TimeTravelDebugPanel } from './TimeTravelDebugPanel';
import { PerformanceSuggestionsPanel } from './PerformanceSuggestionsPanel';
import { MetricsDashboardPanel } from './MetricsDashboardPanel';

export interface ExecutionMonitorProps {
  workflowId: string;
  onExecutionComplete: (status: WorkflowExecutionStatus) => void;
  onStepError: (stepId: string, error: Error) => void;
}

export const ExecutionMonitor: React.FC<ExecutionMonitorProps> = ({
  workflowId,
  onExecutionComplete,
  onStepError
}) => {
  const {
    status,
    progress,
    currentStep,
    error,
    startExecution,
    stopExecution,
    resetExecution
  } = useWorkflowExecution(workflowId);

  const [executionTime, setExecutionTime] = useState<number>(0);
  const [timer, setTimer] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (status === 'RUNNING' && !timer) {
      const newTimer = setInterval(() => {
        setExecutionTime(prev => prev + 1);
      }, 1000);
      setTimer(newTimer);
    } else if (status !== 'RUNNING' && timer) {
      clearInterval(timer);
      setTimer(null);
    }

    if (status === 'COMPLETED' || status === 'FAILED') {
      onExecutionComplete?.(status);
    }

    return () => {
      if (timer) {
        clearInterval(timer);
      }
    };
  }, [status, timer, onExecutionComplete]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = () => {
    switch (status) {
      case 'RUNNING':
        return 'primary.main';
      case 'COMPLETED':
        return 'success.main';
      case 'FAILED':
        return 'error.main';
      default:
        return 'text.secondary';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'RUNNING':
        return <CircularProgress size={20} />;
      case 'COMPLETED':
        return <CheckCircle color="success" />;
      case 'FAILED':
        return <ErrorIcon color="error" />;
      default:
        return null;
    }
  };

  return (
    <>
      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6">Execution Monitor</Typography>
          <Box display="flex" gap={1}>
            <Tooltip title="Start Execution">
              <IconButton
                onClick={startExecution}
                disabled={status === 'RUNNING'}
                color="primary"
              >
                <PlayArrow />
              </IconButton>
            </Tooltip>
            <Tooltip title="Stop Execution">
              <IconButton
                onClick={stopExecution}
                disabled={status !== 'RUNNING'}
                color="error"
              >
                <Stop />
              </IconButton>
            </Tooltip>
            <Tooltip title="Reset Execution">
              <IconButton
                onClick={resetExecution}
                disabled={status === 'RUNNING'}
                color="default"
              >
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {getStatusIcon()}
            <Typography
              variant="body1"
              sx={{ color: getStatusColor() }}
            >
              {status}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Time: {formatTime(executionTime)}
          </Typography>
        </Box>

        {status === 'RUNNING' && (
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Progress: {progress}%
            </Typography>
            <Box
              sx={{
                width: '100%',
                height: 8,
                bgcolor: 'grey.200',
                borderRadius: 1,
                overflow: 'hidden'
              }}
            >
              <Box
                sx={{
                  width: `${progress}%`,
                  height: '100%',
                  bgcolor: 'primary.main',
                  transition: 'width 0.3s ease-in-out'
                }}
              />
            </Box>
          </Box>
        )}

        {currentStep && (
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary">
              Current Step: {currentStep.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {currentStep.description}
            </Typography>
          </Box>
        )}

        {error && (
          <Box
            sx={{
              p: 1,
              bgcolor: 'error.light',
              borderRadius: 1,
              color: 'error.contrastText'
            }}
          >
            <Typography variant="body2">
              Error: {error.message}
            </Typography>
            {error.details && (
              <Typography variant="caption" component="pre" sx={{ mt: 1 }}>
                {error.details}
              </Typography>
            )}
          </Box>
        )}
      </Paper>
      <ResourceUsagePanel />
      <TimeTravelDebugPanel />
      <PerformanceSuggestionsPanel />
      <MetricsDashboardPanel />
    </>
  );
}; 