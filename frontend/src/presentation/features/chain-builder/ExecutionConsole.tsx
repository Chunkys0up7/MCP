import React from 'react';
import { Box, Typography, Divider, /* Button, */ Paper, CircularProgress, Alert } from '@mui/material';

interface LogEntry {
  type: 'info' | 'error' | 'success' | string;
  message: string;
}

interface ExecutionConsoleProps {
  loading?: boolean;
  error?: string | null;
  logs?: (LogEntry | string)[];
}

const ExecutionConsole: React.FC<ExecutionConsoleProps> = ({ loading, error, logs }) => {
  // Normalize logs to LogEntry[]
  const normalizedLogs: LogEntry[] = (logs || []).map((log) =>
    typeof log === 'string' ? { type: 'info', message: log } : log
  );

  return (
    <Paper sx={{ width: '100%', p: 2, bgcolor: 'background.paper', borderTop: '1px solid #E5E7EB', minHeight: 120 }} elevation={2}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6" sx={{ flex: 1, fontWeight: 600 }}>
          Execution Console
        </Typography>
        {loading && <CircularProgress size={24} sx={{ ml: 2 }} />}
      </Box>
      <Divider sx={{ mb: 1 }} />
      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}
      <Box sx={{ maxHeight: 80, overflowY: 'auto' }}>
        {normalizedLogs.map((log, idx) => (
          <Typography
            key={idx}
            variant="body2"
            sx={{
              color:
                log.type === 'error'
                  ? 'error.main'
                  : log.type === 'success'
                  ? 'success.main'
                  : 'text.primary',
              mb: 0.5,
            }}
          >
            {log.message}
          </Typography>
        ))}
        {!loading && normalizedLogs.length === 0 && !error && (
          <Typography variant="body2" color="text.secondary">
            No logs yet.
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default ExecutionConsole; 