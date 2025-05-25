// MetricsDashboardPanel.tsx
// UI skeleton for real-time metrics dashboard for workflow execution.
// TODO: Integrate with backend for live metrics.

import React from 'react';
import { Box, Paper, Typography, Grid, LinearProgress } from '@mui/material';

const mockMetrics = [
  { label: 'CPU Usage', value: 54, unit: '%', color: 'primary' },
  { label: 'Memory Usage', value: 72, unit: '%', color: 'info' },
  { label: 'Throughput', value: 120, unit: 'ops/min', color: 'success' },
];

export const MetricsDashboardPanel: React.FC = () => {
  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Real-Time Metrics Dashboard (Mock)
      </Typography>
      <Grid container spacing={2}>
        {mockMetrics.map((m, idx) => (
          <Grid item xs={12} sm={4} key={idx}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {m.label}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: '100%' }}>
                <LinearProgress variant="determinate" value={m.value} color={m.color as any} sx={{ height: 10, borderRadius: 1 }} />
              </Box>
              <Typography variant="body2" color="text.secondary">
                {m.value} {m.unit}
              </Typography>
            </Box>
          </Grid>
        ))}
      </Grid>
      <Typography variant="caption" color="text.secondary">
        {/* Developer note: Replace mock data with backend metrics. */}
        Data shown is for demonstration only.
      </Typography>
    </Paper>
  );
}; 