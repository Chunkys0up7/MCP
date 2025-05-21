import React from 'react';
import { Box, Typography } from '@mui/material';

const ChainBuilder: React.FC = () => {
  return (
    <Box p={4}>
      <Typography variant="h4">Chain Builder</Typography>
      <Typography variant="body1" mt={2}>
        This is where you will visually build and configure your MCP chains.
      </Typography>
    </Box>
  );
};

export default ChainBuilder; 