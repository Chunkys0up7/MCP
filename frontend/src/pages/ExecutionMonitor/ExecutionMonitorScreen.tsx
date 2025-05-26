import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, Typography, Button, CircularProgress, Alert } from '@mui/material';
import { GanttChart } from '../../presentation/features/workflow-builder/GanttChart';
import { useWebSocket } from '../../application/hooks/useWebSocket';
import { useWorkflowStore } from '../../application/stores/workflowStore';

export const ExecutionMonitorScreen: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const { nodes } = useWorkflowStore();
  const workflowId = 'demo-workflow'; // This should come from props or context in a real app
  const [isLoading, setIsLoading] = useState(false); // Future: set true when loading
  const [error, setError] = useState<string | null>(null); // Future: set error message

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Global loading and error states */}
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 6 }} role="status" aria-busy="true">
          <CircularProgress size={40} />
          <Box sx={{ ml: 2 }}>Loading execution data...</Box>
        </Box>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} role="alert">{error}</Alert>
      )}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 6 }}>
        <Typography variant="h4" fontWeight={700}>
          Workflow Execution Monitor
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Current Time: {currentTime.toLocaleTimeString()}
        </Typography>
      </Box>
      <Paper sx={{ mb: 6, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: 'grey.50', borderRadius: 2, boxShadow: 1 }}>
        <Typography color="text.primary">
          Workflow: <Box component="span" fontWeight={600} display="inline">Demo_CreditApproval_v1.2</Box>
        </Typography>
        <Button variant="contained" color="primary" size="small" sx={{ fontWeight: 500, borderRadius: 1 }}>
          Select Workflow
        </Button>
      </Paper>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, height: 400 }}>
            {nodes && nodes.length === 0 ? (
              <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }} role="region" aria-label="No Execution Data">
                <Typography color="text.secondary" fontSize={20} mb={2}>No execution data to display.</Typography>
                <Typography color="text.secondary">Start a workflow run to see execution progress here.</Typography>
              </Box>
            ) : (
              <GanttChart workflowId={workflowId} />
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExecutionMonitorScreen; 