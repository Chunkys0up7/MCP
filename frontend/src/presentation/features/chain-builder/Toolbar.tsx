import React from 'react';
import {
  AppBar,
  Toolbar as MuiToolbar,
  IconButton,
  Typography,
  Box,
  Button,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import UndoIcon from '@mui/icons-material/Undo';
import RedoIcon from '@mui/icons-material/Redo';
import ViewSidebarIcon from '@mui/icons-material/ViewSidebar';
import MenuIcon from '@mui/icons-material/Menu';

interface ToolbarProps {
  onSave: () => Promise<void>;
  onExecute: () => Promise<void>;
  onStop?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  onToggleProperties: () => void;
  onToggleLibrary: () => void;
  isLoading?: boolean;
  isExecuting?: boolean;
  canUndo?: boolean;
  canRedo?: boolean;
}

const Toolbar: React.FC<ToolbarProps> = ({
  onSave,
  onExecute,
  onStop,
  onUndo,
  onRedo,
  onToggleProperties,
  onToggleLibrary,
  isLoading = false,
  isExecuting = false,
  canUndo = false,
  canRedo = false,
}) => {
  return (
    <AppBar position="static" color="default" elevation={1}>
      <MuiToolbar variant="dense">
        <Tooltip title="Toggle MCP Library">
          <IconButton onClick={onToggleLibrary} size="small">
            <MenuIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Toggle Properties Panel">
          <IconButton onClick={onToggleProperties} size="small">
            <ViewSidebarIcon />
          </IconButton>
        </Tooltip>
        <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 2 }}>
          MCP Workflow
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {onUndo && (
            <Tooltip title="Undo (Ctrl+Z)">
              <span>
                <IconButton
                  onClick={onUndo}
                  disabled={!canUndo || isLoading}
                  size="small"
                >
                  <UndoIcon />
                </IconButton>
              </span>
            </Tooltip>
          )}
          {onRedo && (
            <Tooltip title="Redo (Ctrl+Y)">
              <span>
                <IconButton
                  onClick={onRedo}
                  disabled={!canRedo || isLoading}
                  size="small"
                >
                  <RedoIcon />
                </IconButton>
              </span>
            </Tooltip>
          )}
          <Tooltip title="Save (Ctrl+S)">
            <span>
              <Button
                variant="outlined"
                startIcon={isLoading ? <CircularProgress size={20} /> : <SaveIcon />}
                onClick={onSave}
                disabled={isLoading}
                size="small"
              >
                Save
              </Button>
            </span>
          </Tooltip>
          {isExecuting ? (
            <Tooltip title="Stop Execution">
              <span>
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<StopIcon />}
                  onClick={onStop}
                  disabled={isLoading}
                  size="small"
                >
                  Stop
                </Button>
              </span>
            </Tooltip>
          ) : (
            <Tooltip title="Execute Workflow">
              <span>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<PlayArrowIcon />}
                  onClick={onExecute}
                  disabled={isLoading}
                  size="small"
                >
                  Execute
                </Button>
              </span>
            </Tooltip>
          )}
        </Box>
      </MuiToolbar>
    </AppBar>
  );
};

export default Toolbar; 