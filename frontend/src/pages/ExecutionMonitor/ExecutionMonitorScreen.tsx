import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, Typography, Button, CircularProgress, Alert, Tabs, Tab } from '@mui/material';
import { GanttChart } from '../../presentation/features/workflow-builder/GanttChart';
import { useWebSocket } from '../../application/hooks/useWebSocket';
import { useWorkflowStore } from '../../application/stores/workflowStore';

export const ExecutionMonitorScreen: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const { nodes } = useWorkflowStore();
  const workflowId = 'demo-workflow'; // This should come from props or context in a real app
  const [isLoading] = useState(false); // Future: set true when loading
  const [error] = useState<string | null>(null); // Future: set error message
  const [tab, setTab] = useState(0);
  const ws = useWebSocket(workflowId);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => setTab(newValue);

  // Logs panel: use WebSocket errors as mock logs for now
  const logs = ws.errors.map((err, idx) => `Error ${idx + 1}: ${err}`);

  // Metrics panel: use latest resource update
  const metrics = ws.getLatestResourceUpdate();

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Onboarding tip */}
      <Alert severity="info" sx={{ mb: 3 }} role="region" aria-label="Onboarding Tip">
        Welcome to the Execution Monitor! Track workflow progress in real time, view logs and metrics, and access advanced debugging tools. All panels are fully responsive and accessible.
      </Alert>
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
          <Paper sx={{ p: 2, height: 400, mb: 4 }}>
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
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Tabs value={tab} onChange={handleTabChange} aria-label="Execution Monitor Tabs">
              <Tab label="Logs" id="tab-logs" aria-controls="tabpanel-logs" />
              <Tab label="Metrics" id="tab-metrics" aria-controls="tabpanel-metrics" />
              <Tab label="Resource Adjuster" id="tab-resource" aria-controls="tabpanel-resource" />
              <Tab label="Time Travel Debugger" id="tab-debugger" aria-controls="tabpanel-debugger" />
            </Tabs>
            {/* Logs Panel */}
            {tab === 0 && (
              <Box role="tabpanel" id="tabpanel-logs" aria-labelledby="tab-logs" sx={{ mt: 2, minHeight: 120 }}>
                {logs.length === 0 ? (
                  <Alert severity="info">No logs yet. Workflow logs will appear here in real time.</Alert>
                ) : (
                  <Box sx={{ maxHeight: 200, overflow: 'auto', fontFamily: 'monospace', fontSize: 14 }}>
                    {logs.map((log, idx) => (
                      <Box key={idx} sx={{ mb: 1 }}>{log}</Box>
                    ))}
                  </Box>
                )}
              </Box>
            )}
            {/* Metrics Panel */}
            {tab === 1 && (
              <Box role="tabpanel" id="tabpanel-metrics" aria-labelledby="tab-metrics" sx={{ mt: 2, minHeight: 120 }}>
                {metrics ? (
                  <Box>
                    <Typography variant="subtitle1" fontWeight={600}>Resource Usage</Typography>
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2">CPU: {metrics.cpu}%</Typography>
                      <Typography variant="body2">Memory: {metrics.memory} MB</Typography>
                      <Typography variant="body2">Network In: {metrics.network.bytesIn} bytes</Typography>
                      <Typography variant="body2">Network Out: {metrics.network.bytesOut} bytes</Typography>
                    </Box>
                  </Box>
                ) : (
                  <Alert severity="info">No resource metrics available yet.</Alert>
                )}
              </Box>
            )}
            {/* Resource Adjuster Panel */}
            {tab === 2 && (
              <Box role="tabpanel" id="tabpanel-resource" aria-labelledby="tab-resource" sx={{ mt: 2, minHeight: 120 }}>
                <Alert severity="info">Resource adjustment UI coming soon. Here you will be able to adjust CPU, memory, and other resources for workflow execution.</Alert>
              </Box>
            )}
            {/* Time Travel Debugger Panel */}
            {tab === 3 && (
              <Box role="tabpanel" id="tabpanel-debugger" aria-labelledby="tab-debugger" sx={{ mt: 2, minHeight: 120 }}>
                <Alert severity="info">Time travel debugger UI coming soon. Here you will be able to step through workflow execution history.</Alert>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExecutionMonitorScreen; 