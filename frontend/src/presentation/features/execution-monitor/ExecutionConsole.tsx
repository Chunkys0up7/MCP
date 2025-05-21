import React, { useState } from 'react';
import { Box, Typography, IconButton, TextField, Paper } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import ClearIcon from '@mui/icons-material/Clear';
import { useChainStore } from '../../../infrastructure/state/chainStore';

interface LogEntry {
  timestamp: string;
  type: 'info' | 'error' | 'success';
  message: string;
}

const ExecutionConsole: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const addLog = (type: LogEntry['type'], message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, type, message }]);
  };

  const handleExecute = () => {
    setIsRunning(true);
    addLog('info', 'Starting chain execution...');
    
    // TODO: Implement actual chain execution logic
    setTimeout(() => {
      addLog('success', 'Chain execution completed successfully');
      setIsRunning(false);
    }, 2000);
  };

  const handleStop = () => {
    setIsRunning(false);
    addLog('info', 'Chain execution stopped');
  };

  const handleClear = () => {
    setLogs([]);
  };

  const getLogColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'error':
        return 'error.main';
      case 'success':
        return 'success.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Console Controls */}
      <Box sx={{ 
        p: 1, 
        display: 'flex', 
        gap: 1, 
        borderBottom: 1, 
        borderColor: 'divider',
        bgcolor: 'background.default'
      }}>
        <IconButton 
          color="primary" 
          size="small" 
          onClick={handleExecute}
          disabled={isRunning}
        >
          <PlayArrowIcon />
        </IconButton>
        <IconButton 
          color="error" 
          size="small" 
          onClick={handleStop}
          disabled={!isRunning}
        >
          <StopIcon />
        </IconButton>
        <IconButton 
          color="default" 
          size="small" 
          onClick={handleClear}
        >
          <ClearIcon />
        </IconButton>
      </Box>

      {/* Log Output */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'auto', 
        p: 1,
        fontFamily: 'Fira Code, monospace',
        fontSize: '0.875rem',
        bgcolor: 'background.default'
      }}>
        {logs.map((log, index) => (
          <Box 
            key={index} 
            sx={{ 
              display: 'flex', 
              gap: 1,
              color: getLogColor(log.type),
              mb: 0.5
            }}
          >
            <Typography 
              component="span" 
              sx={{ 
                color: 'text.secondary',
                fontFamily: 'inherit',
                fontSize: 'inherit'
              }}
            >
              [{log.timestamp}]
            </Typography>
            <Typography 
              component="span" 
              sx={{ 
                fontFamily: 'inherit',
                fontSize: 'inherit'
              }}
            >
              {log.message}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default ExecutionConsole; 