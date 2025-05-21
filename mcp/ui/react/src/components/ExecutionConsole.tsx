import React from 'react';
import { Box, Typography } from '@mui/material';

const ExecutionConsole: React.FC = () => {
  return (
    <Box p={2} borderTop={1} borderColor="divider">
      <Typography variant="subtitle1">Execution Console</Typography>
      <Typography variant="body2" mt={1}>
        Real-time execution logs and status will appear here.
      </Typography>
    </Box>
  );
};

export default ExecutionConsole; 