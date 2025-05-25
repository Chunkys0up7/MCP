// ResourceUsagePanel.tsx
// Panel to display resource usage (CPU, memory, etc.) for workflow steps.
// TODO: Integrate with backend API when available (e.g., /workflows/runs/{run_id}/resource-usage or step details)

import React from 'react';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, LinearProgress } from '@mui/material';

export interface ResourceUsage {
  stepId: string;
  label: string;
  cpu: number; // percent
  memory: number; // MB
  // Add more fields as needed (disk, GPU, etc.)
}

interface ResourceUsagePanelProps {
  data?: ResourceUsage[]; // Optional mock data
}

// Example mock data
const exampleResourceUsage: ResourceUsage[] = [
  { stepId: 'step-1', label: 'Step 1', cpu: 32, memory: 120 },
  { stepId: 'step-2', label: 'Step 2', cpu: 68, memory: 210 },
  { stepId: 'step-3', label: 'Step 3', cpu: 15, memory: 80 },
];

export const ResourceUsagePanel: React.FC<ResourceUsagePanelProps> = ({ data }) => {
  const usageData = data || exampleResourceUsage;

  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Resource Usage (Mock Data)
      </Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Step</TableCell>
              <TableCell align="right">CPU (%)</TableCell>
              <TableCell align="right">Memory (MB)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {usageData.map((row) => (
              <TableRow key={row.stepId}>
                <TableCell>{row.label}</TableCell>
                <TableCell align="right">
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: 60, mr: 1 }}>
                      <LinearProgress variant="determinate" value={row.cpu} sx={{ height: 8, borderRadius: 1 }} />
                    </Box>
                    <Typography variant="body2" color="text.secondary">{row.cpu}%</Typography>
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: 60, mr: 1 }}>
                      <LinearProgress variant="determinate" value={Math.min(row.memory / 4, 100)} sx={{ height: 8, borderRadius: 1, bgcolor: 'info.light' }} />
                    </Box>
                    <Typography variant="body2" color="text.secondary">{row.memory} MB</Typography>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Typography variant="caption" color="text.secondary">
        {/* Developer note: Replace mock data with backend integration when available. */}
        Data shown is for demonstration only. Future: fetch from backend and support more metrics.
      </Typography>
    </Paper>
  );
}; 