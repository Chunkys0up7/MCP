import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, Typography, Button } from '@mui/material';
import { GanttChart } from '../../presentation/features/workflow-builder/GanttChart';
import { useWebSocket } from '../../application/hooks/useWebSocket';
import { useWorkflowStore } from '../../application/stores/workflowStore';

export const ExecutionMonitorScreen: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const { nodes } = useWorkflowStore();
  const workflowId = 'demo-workflow'; // This should come from props or context in a real app

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="p-4 md:p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl md:text-3xl font-bold">Workflow Execution Monitor</h1>
        <div className="text-sm text-gray-600">
          Current Time: {currentTime.toLocaleTimeString()}
        </div>
      </div>
      
      <div className="mb-6 p-3 bg-gray-50 rounded-md shadow-sm flex justify-between items-center">
        <span className="text-gray-700">Workflow: <span className="font-semibold">Demo_CreditApproval_v1.2</span></span>
        <button className="px-3 py-1.5 bg-indigo-600 text-white text-xs font-medium rounded hover:bg-indigo-700">
          Select Workflow
        </button>
      </div>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, height: 400 }}>
            <GanttChart workflowId={workflowId} />
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
}; 