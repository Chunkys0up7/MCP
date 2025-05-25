import React, { useState } from 'react';
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
  Divider,
  LinearProgress
} from '@mui/material';
import {
  CheckCircle as ValidIcon,
  Error as InvalidIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Speed as CpuIcon,
  NetworkCheck as NetworkIcon
} from '@mui/icons-material';
import { useDAGOptimization } from '../../../application/hooks/useDAGOptimization';
import { useWorkflowStore } from '../../../infrastructure/state/workflowStore';

export const OptimizationPanel: React.FC = () => {
  const { nodes, edges } = useWorkflowStore();
  const {
    isValid,
    cycles,
    parallelGroups,
    costEstimate,
    suggestions,
    optimize
  } = useDAGOptimization(nodes, edges);

  const [expanded, setExpanded] = useState(true);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const formatMetric = (value: number, unit: string) => {
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}k ${unit}`;
    }
    return `${value.toFixed(1)} ${unit}`;
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
        <Typography variant="h6">
          Workflow Optimization
          <Box component="span" sx={{ ml: 1 }}>
            {isValid ? (
              <ValidIcon color="success" fontSize="small" />
            ) : (
              <InvalidIcon color="error" fontSize="small" />
            )}
          </Box>
        </Typography>
        <Box>
          <Tooltip title="Refresh">
            <IconButton size="small" onClick={optimize}>
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
          {/* Cost Estimates */}
          <Typography variant="subtitle2" gutterBottom>
            Cost Estimates
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon>
                <SpeedIcon />
              </ListItemIcon>
              <ListItemText
                primary="Execution Time"
                secondary={formatMetric(costEstimate.executionTime, 'ms')}
              />
              <LinearProgress
                variant="determinate"
                value={Math.min((costEstimate.executionTime / 1000) * 100, 100)}
                sx={{ width: 100 }}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <MemoryIcon />
              </ListItemIcon>
              <ListItemText
                primary="Memory Usage"
                secondary={formatMetric(costEstimate.memoryUsage, 'MB')}
              />
              <LinearProgress
                variant="determinate"
                value={Math.min((costEstimate.memoryUsage / 500) * 100, 100)}
                sx={{ width: 100 }}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CpuIcon />
              </ListItemIcon>
              <ListItemText
                primary="CPU Usage"
                secondary={`${costEstimate.cpuUsage.toFixed(1)}%`}
              />
              <LinearProgress
                variant="determinate"
                value={costEstimate.cpuUsage}
                sx={{ width: 100 }}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <NetworkIcon />
              </ListItemIcon>
              <ListItemText
                primary="Network Cost"
                secondary={formatMetric(costEstimate.networkCost, 'MB')}
              />
              <LinearProgress
                variant="determinate"
                value={Math.min((costEstimate.networkCost / 100) * 100, 100)}
                sx={{ width: 100 }}
              />
            </ListItem>
          </List>

          <Divider sx={{ my: 2 }} />

          {/* Parallel Groups */}
          {parallelGroups.length > 0 && (
            <>
              <Typography variant="subtitle2" gutterBottom>
                Parallel Execution Groups
              </Typography>
              <List dense>
                {parallelGroups.map((group, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={`Group ${index + 1}`}
                      secondary={group.join(', ')}
                    />
                  </ListItem>
                ))}
              </List>
              <Divider sx={{ my: 2 }} />
            </>
          )}

          {/* Cycles */}
          {cycles.length > 0 && (
            <>
              <Typography variant="subtitle2" color="error" gutterBottom>
                Detected Cycles
              </Typography>
              <List dense>
                {cycles.map((cycle, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={`Cycle ${index + 1}`}
                      secondary={cycle.join(' → ')}
                    />
                  </ListItem>
                ))}
              </List>
              <Divider sx={{ my: 2 }} />
            </>
          )}

          {/* Optimization Suggestions */}
          {suggestions.length > 0 && (
            <>
              <Typography variant="subtitle2" gutterBottom>
                Optimization Suggestions
              </Typography>
              <List dense>
                {suggestions.map((suggestion, index) => (
                  <ListItem key={index}>
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