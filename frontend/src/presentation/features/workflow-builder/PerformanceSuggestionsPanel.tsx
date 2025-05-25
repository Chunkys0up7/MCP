// PerformanceSuggestionsPanel.tsx
// UI skeleton for workflow performance suggestions and bottleneck detection.
// TODO: Integrate with backend for real suggestions and analysis.

import React from 'react';
import { Box, Paper, Typography, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { TrendingUp, WarningAmber } from '@mui/icons-material';

const mockSuggestions = [
  { icon: <TrendingUp color="success" />, text: 'Step 2 can be parallelized for faster execution.' },
  { icon: <WarningAmber color="warning" />, text: 'Step 3 is a bottleneck (high memory usage).' },
  { icon: <TrendingUp color="info" />, text: 'Consider increasing CPU for Step 1 to reduce latency.' },
];

export const PerformanceSuggestionsPanel: React.FC = () => {
  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Performance Suggestions (Mock)
      </Typography>
      <List>
        {mockSuggestions.map((s, idx) => (
          <ListItem key={idx}>
            <ListItemIcon>{s.icon}</ListItemIcon>
            <ListItemText primary={s.text} />
          </ListItem>
        ))}
      </List>
      <Typography variant="caption" color="text.secondary">
        {/* Developer note: Replace mock data with backend analysis and suggestions. */}
        Data shown is for demonstration only.
      </Typography>
    </Paper>
  );
}; 