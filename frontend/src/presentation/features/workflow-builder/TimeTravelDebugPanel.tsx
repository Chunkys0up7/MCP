// TimeTravelDebugPanel.tsx
// UI skeleton for time-travel debugging of workflow steps.
// TODO: Integrate with backend to fetch step state/history.

import React, { useState } from 'react';
import { Box, Paper, Typography, Slider, Select, MenuItem } from '@mui/material';

const mockSteps = [
  { id: 'step-1', label: 'Step 1', state: 'Input: 42, Output: 84' },
  { id: 'step-2', label: 'Step 2', state: 'Input: 84, Output: 168' },
  { id: 'step-3', label: 'Step 3', state: 'Input: 168, Output: 336' },
];

export const TimeTravelDebugPanel: React.FC = () => {
  const [selectedStep, setSelectedStep] = useState(0);

  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Time-Travel Debugging (Mock)
      </Typography>
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2">Select Step:</Typography>
        <Select
          value={selectedStep}
          onChange={e => setSelectedStep(Number(e.target.value))}
          size="small"
        >
          {mockSteps.map((step, idx) => (
            <MenuItem key={step.id} value={idx}>{step.label}</MenuItem>
          ))}
        </Select>
      </Box>
      <Box>
        <Typography variant="body2" color="text.secondary">
          State at <b>{mockSteps[selectedStep].label}</b>:
        </Typography>
        <Typography variant="body1" sx={{ mt: 1 }}>
          {mockSteps[selectedStep].state}
        </Typography>
      </Box>
      <Typography variant="caption" color="text.secondary">
        {/* Developer note: Replace mock data with backend integration for step state/history. */}
        Data shown is for demonstration only.
      </Typography>
    </Paper>
  );
}; 