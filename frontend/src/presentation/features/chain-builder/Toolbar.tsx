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
      <MuiToolbar
        variant="dense"
        tabIndex={0}
        role="toolbar"
        aria-label="Workflow Actions Toolbar"
        aria-describedby="toolbar-instructions"
        sx={{ outline: 'none' }}
        onFocus={e => e.currentTarget.style.outline = '2px solid #1976d2'}
        onBlur={e => e.currentTarget.style.outline = 'none'}
      >
        <div id="toolbar-instructions" style={{ position: 'absolute', left: -9999, top: 'auto', width: 1, height: 1, overflow: 'hidden' }}>
          Use Tab to navigate toolbar actions. Each button is labeled for screen readers.
        </div>
        <Tooltip title="Toggle MCP Library">
          <IconButton onClick={onToggleLibrary} size="small" aria-label="Toggle MCP Library">
            <MenuIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Toggle Properties Panel">
          <IconButton onClick={onToggleProperties} size="small" aria-label="Toggle Properties Panel">
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
                  aria-label="Undo"
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
                  aria-label="Redo"
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
                aria-label="Save Workflow"
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
                  aria-label="Stop Execution"
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
                  aria-label="Execute Workflow"
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