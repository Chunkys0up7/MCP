import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Collapse,
  Tooltip,
  LinearProgress,
  Divider
} from '@mui/material';
import {
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  NetworkCheck as NetworkIcon,
  Storage as StorageIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { usePerformance } from '../../../application/hooks/usePerformance';
import { useWorkflowStore } from '../../../infrastructure/state/workflowStore';

interface PerformancePanelProps {
  workflowId: string;
}

export const PerformancePanel: React.FC<PerformancePanelProps> = ({ workflowId }) => {
  const { nodes, edges } = useWorkflowStore();
  const {
    metrics,
    nodePerformance,
    workflowPerformance,
    cacheStats,
    getBottlenecks,
    getOptimizationSuggestions
  } = usePerformance(workflowId, nodes, edges);

  const [expanded, setExpanded] = React.useState(true);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const bottlenecks = getBottlenecks();
  const suggestions = getOptimizationSuggestions();

  const calculateCacheEfficiency = () => {
    const total = cacheStats.hits + cacheStats.misses;
    return total === 0 ? 0 : (cacheStats.hits / total) * 100;
  };

  return (
    <Paper
      elevation={2}
      sx={{
        position: 'absolute',
        top: 16,
        right: 16,
        width: 400,
        maxHeight: 600,
        overflow: 'auto',
        zIndex: 1000
      }}
    >
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: 1,
          borderColor: 'divider'
        }}
      >
        <Typography variant="h6">Performance Monitor</Typography>
        <Box>
          <Tooltip title="Refresh">
            <IconButton size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <IconButton onClick={handleExpandClick} size="small">
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
      </Box>

      <Collapse in={expanded}>
        <Box sx={{ p: 2 }}>
          {/* Overall Performance */}
          <Typography variant="subtitle1" gutterBottom>
            Overall Performance
          </Typography>
          {workflowPerformance && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Total Execution Time: {workflowPerformance.totalExecutionTime}ms
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Network Latency: {workflowPerformance.networkLatency}ms
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Data Transfer: {(workflowPerformance.dataTransferSize / 1024).toFixed(2)} KB
              </Typography>
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          {/* Cache Performance */}
          <Typography variant="subtitle1" gutterBottom>
            Cache Performance
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <StorageIcon sx={{ mr: 1 }} />
              <Typography variant="body2">
                Cache Efficiency: {calculateCacheEfficiency().toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={calculateCacheEfficiency()}
              sx={{ height: 8, borderRadius: 1 }}
            />
            <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="caption" color="text.secondary">
                Hits: {cacheStats.hits}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Misses: {cacheStats.misses}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Node Performance */}
          <Typography variant="subtitle1" gutterBottom>
            Node Performance
          </Typography>
          <List dense>
            {Object.entries(nodePerformance).map(([nodeId, performance]) => (
              <ListItem key={nodeId}>
                <ListItemIcon>
                  <SpeedIcon />
                </ListItemIcon>
                <ListItemText
                  primary={`Node ${nodeId}`}
                  secondary={
                    <>
                      <Typography variant="caption" component="div">
                        Execution Time: {performance.executionTime}ms
                      </Typography>
                      <Typography variant="caption" component="div">
                        Network Requests: {performance.networkRequests}
                      </Typography>
                      <Typography variant="caption" component="div">
                        Cache Hits: {performance.cacheHits}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>

          {/* Bottlenecks */}
          {bottlenecks.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" color="warning.main" gutterBottom>
                Performance Bottlenecks
              </Typography>
              <List dense>
                {bottlenecks.map((nodeId) => (
                  <ListItem key={nodeId}>
                    <ListItemIcon>
                      <MemoryIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText
                      primary={`Node ${nodeId}`}
                      secondary="High execution time detected"
                    />
                  </ListItem>
                ))}
              </List>
            </>
          )}

          {/* Optimization Suggestions */}
          {suggestions.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" color="info.main" gutterBottom>
                Optimization Suggestions
              </Typography>
              <List dense>
                {suggestions.map((suggestion, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <NetworkIcon color="info" />
                    </ListItemIcon>
                    <ListItemText primary={suggestion} />
                  </ListItem>
                ))}
              </List>
            </>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
}; 