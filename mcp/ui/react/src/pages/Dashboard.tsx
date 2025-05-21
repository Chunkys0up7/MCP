import React from 'react';
import { Box, Typography } from '@mui/material';

const Dashboard: React.FC = () => {
  return (
    <Box p={4}>
      <Typography variant="h4">Dashboard</Typography>
      <Typography variant="body1" mt={2}>
        Welcome to the MCP Chain Builder Dashboard. Select a chain or create a new one to get started.
      </Typography>
    </Box>
  );
};

export default Dashboard; 