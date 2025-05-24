import React, { useMemo } from 'react';
import { Box, Paper, Typography, useTheme } from '@mui/material';
import { useWorkflowStore } from '../../../application/stores/workflowStore';
import { useWebSocket } from '../../../application/hooks/useWebSocket';
import { WorkflowExecutionStatus } from '../../../domain/models/workflow';

interface GanttChartProps {
  workflowId: string;
}

interface TaskBar {
  id: string;
  label: string;
  startTime: number;
  endTime: number;
  status: WorkflowExecutionStatus;
  dependencies: string[];
}

export const GanttChart: React.FC<GanttChartProps> = ({ workflowId }) => {
  const theme = useTheme();
  const { nodes, edges } = useWorkflowStore();
  const { getNodeStatus, getLatestResourceUpdate } = useWebSocket(workflowId);

  // Calculate task bars for the Gantt chart
  const taskBars = useMemo(() => {
    return nodes.map(node => {
      const status = getNodeStatus(node.id);
      const startTime = status?.startTime ? new Date(status.startTime).getTime() : 0;
      const endTime = status?.endTime ? new Date(status.endTime).getTime() : 0;
      
      // Get dependencies from edges
      const dependencies = edges
        .filter(edge => edge.target === node.id)
        .map(edge => edge.source);

      return {
        id: node.id,
        label: node.data.label,
        startTime,
        endTime: endTime || startTime + 1000, // If not ended, show current progress
        status: status?.status || 'PENDING',
        dependencies
      };
    });
  }, [nodes, edges, getNodeStatus]);

  // Calculate chart dimensions
  const chartHeight = taskBars.length * 40 + 60; // 40px per task + padding
  const minTime = Math.min(...taskBars.map(t => t.startTime));
  const maxTime = Math.max(...taskBars.map(t => t.endTime));
  const timeRange = maxTime - minTime;

  const getStatusColor = (status: WorkflowExecutionStatus) => {
    switch (status) {
      case 'RUNNING':
        return theme.palette.primary.main;
      case 'COMPLETED':
        return theme.palette.success.main;
      case 'FAILED':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[300];
    }
  };

  return (
    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Execution Timeline
      </Typography>
      
      <Box sx={{ position: 'relative', height: chartHeight }}>
        {/* Time markers */}
        <Box sx={{ 
          position: 'absolute', 
          top: 0, 
          left: 0, 
          right: 0, 
          height: 30,
          borderBottom: 1,
          borderColor: 'divider'
        }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                left: `${(i * 25)}%`,
                top: 0,
                height: '100%',
                borderLeft: 1,
                borderColor: 'divider',
                display: 'flex',
                alignItems: 'flex-end',
                pb: 0.5
              }}
            >
              <Typography variant="caption" color="text.secondary">
                {new Date(minTime + (timeRange * i / 4)).toLocaleTimeString()}
              </Typography>
            </Box>
          ))}
        </Box>

        {/* Task bars */}
        {taskBars.map((task, index) => {
          const left = ((task.startTime - minTime) / timeRange) * 100;
          const width = ((task.endTime - task.startTime) / timeRange) * 100;
          
          return (
            <Box
              key={task.id}
              sx={{
                position: 'absolute',
                top: 40 + (index * 40),
                left: `${left}%`,
                width: `${width}%`,
                height: 30,
                bgcolor: getStatusColor(task.status),
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                px: 1,
                color: 'white',
                fontSize: '0.875rem',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {task.label}
            </Box>
          );
        })}

        {/* Dependency lines */}
        {taskBars.map(task => {
          return task.dependencies.map(depId => {
            const sourceTask = taskBars.find(t => t.id === depId);
            if (!sourceTask) return null;

            const sourceIndex = taskBars.findIndex(t => t.id === depId);
            const targetIndex = taskBars.findIndex(t => t.id === task.id);
            
            const sourceLeft = ((sourceTask.endTime - minTime) / timeRange) * 100;
            const targetLeft = ((task.startTime - minTime) / timeRange) * 100;
            
            return (
              <Box
                key={`${depId}-${task.id}`}
                sx={{
                  position: 'absolute',
                  top: 40 + (sourceIndex * 40) + 15,
                  left: `${sourceLeft}%`,
                  width: `${targetLeft - sourceLeft}%`,
                  height: 2,
                  bgcolor: theme.palette.grey[400],
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    right: 0,
                    top: -4,
                    width: 0,
                    height: 0,
                    borderTop: '5px solid transparent',
                    borderBottom: '5px solid transparent',
                    borderLeft: `5px solid ${theme.palette.grey[400]}`
                  }
                }}
              />
            );
          });
        })}
      </Box>
    </Paper>
  );
}; 