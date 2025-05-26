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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon,
  CheckCircle as ResolveIcon,
  Block as IgnoreIcon
} from '@mui/icons-material';
import { useErrorHandling } from '../../../application/hooks/useErrorHandling';
import { useWorkflowStore } from '../../../infrastructure/state/workflowStore';
import { WorkflowError } from '../../../infrastructure/services/errorHandlingService';

export const ErrorPanel: React.FC = () => {
  const { nodes, edges } = useWorkflowStore();
  const {
    errors,
    errorStats,
    retryError,
    resolveError,
    ignoreError
  } = useErrorHandling(nodes, edges);

  const [expanded, setExpanded] = useState(true);
  const [selectedError, setSelectedError] = useState<WorkflowError | null>(null);
  const [retryDialogOpen, setRetryDialogOpen] = useState(false);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleErrorClick = (error: WorkflowError) => {
    setSelectedError(error);
  };

  const handleRetry = async () => {
    if (selectedError) {
      setRetryDialogOpen(true);
    }
  };

  const handleRetryConfirm = async () => {
    if (selectedError) {
      await retryError(selectedError.id, async () => {
        // Implement retry logic here
        console.log(`Retrying error: ${selectedError.id}`);
      });
      setRetryDialogOpen(false);
      setSelectedError(null);
    }
  };

  const handleResolve = () => {
    if (selectedError) {
      resolveError(selectedError.id);
      setSelectedError(null);
    }
  };

  const handleIgnore = () => {
    if (selectedError) {
      ignoreError(selectedError.id);
      setSelectedError(null);
    }
  };

  const getSeverityIcon = (severity: WorkflowError['severity']) => {
    switch (severity) {
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getSeverityColor = (severity: WorkflowError['severity']) => {
    switch (severity) {
      case 'error':
        return 'error.main';
      case 'warning':
        return 'warning.main';
      case 'info':
        return 'info.main';
      default:
        return 'text.primary';
    }
  };

  const canRetry = (err: WorkflowError | null) => {
    if (!err) return false;
    if (typeof err.retryCount !== 'number' || typeof err.maxRetries !== 'number') return false;
    return err.retryCount < err.maxRetries;
  };

  return (
    <>
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
        tabIndex={0}
        role="region"
        aria-label="Error Monitor Panel"
        aria-describedby="errorpanel-instructions"
        onFocus={e => e.currentTarget.style.outline = '2px solid #d32f2f'}
        onBlur={e => e.currentTarget.style.outline = 'none'}
      >
        <div id="errorpanel-instructions" style={{ position: 'absolute', left: -9999, top: 'auto', width: 1, height: 1, overflow: 'hidden' }}>
          Use Tab to navigate error list and actions. Error list is live-updated for screen readers.
        </div>
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
            Error Monitor
            {errorStats.active > 0 && ` (${errorStats.active} active)`}
          </Typography>
          <Box>
            <Tooltip title="Refresh">
              <IconButton size="small" aria-label="Refresh Error List">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <IconButton onClick={handleExpandClick} size="small" aria-label={expanded ? "Collapse Error Panel" : "Expand Error Panel"}>
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        <Collapse in={expanded}>
          <Box sx={{ p: 2 }}>
            {errors.length > 0 ? (
              <List dense aria-live="polite" aria-label="Error List">
                {errors.map((error) => (
                  <ListItem
                    key={error.id}
                    button
                    onClick={() => handleErrorClick(error)}
                    selected={selectedError?.id === error.id}
                  >
                    <ListItemIcon>
                      {getSeverityIcon(error.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={error.message}
                      secondary={
                        <>
                          <Typography variant="caption" component="div">
                            {error.type} - {error.nodeId ? `Node: ${error.nodeId}` : ''}
                          </Typography>
                          <Typography variant="caption" component="div">
                            {new Date(error.timestamp).toLocaleString()}
                          </Typography>
                        </>
                      }
                      primaryTypographyProps={{
                        color: getSeverityColor(error.severity)
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary" align="center">
                No active errors
              </Typography>
            )}

            {selectedError && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Error Details
                </Typography>
                <Typography variant="body2" paragraph>
                  {selectedError.details?.message || selectedError.message}
                </Typography>
                {selectedError.details?.context && (
                  <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(selectedError.details.context, null, 2)}
                  </Typography>
                )}
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    startIcon={<RefreshIcon />}
                    onClick={handleRetry}
                    aria-label="Retry Error"
                    disabled={!canRetry(selectedError)}
                  >
                    Retry
                  </Button>
                  <Button
                    size="small"
                    startIcon={<ResolveIcon />}
                    onClick={handleResolve}
                    aria-label="Resolve Error"
                  >
                    Resolve
                  </Button>
                  <Button
                    size="small"
                    startIcon={<IgnoreIcon />}
                    onClick={handleIgnore}
                    aria-label="Ignore Error"
                  >
                    Ignore
                  </Button>
                </Box>
              </Box>
            )}
          </Box>
        </Collapse>
      </Paper>

      <Dialog open={retryDialogOpen} onClose={() => setRetryDialogOpen(false)}>
        <DialogTitle>Confirm Retry</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to retry this operation? This will be attempt {selectedError?.retryCount + 1} of {selectedError?.maxRetries}.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRetryDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRetryConfirm} color="primary" variant="contained">
            Retry
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}; 