import React from 'react';
import { AppBar, Toolbar as MuiToolbar, Typography, IconButton } from '@mui/material';
import UndoIcon from '@mui/icons-material/Undo';
import RedoIcon from '@mui/icons-material/Redo';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const Toolbar: React.FC = () => {
  return (
    <AppBar position="static" color="default" elevation={1} sx={{ zIndex: 1201 }}>
      <MuiToolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          MCP Chain Builder
        </Typography>
        <IconButton color="inherit"><UndoIcon /></IconButton>
        <IconButton color="inherit"><RedoIcon /></IconButton>
        <IconButton color="inherit"><ZoomInIcon /></IconButton>
        <IconButton color="inherit"><ZoomOutIcon /></IconButton>
        <IconButton color="primary"><PlayArrowIcon /></IconButton>
      </MuiToolbar>
    </AppBar>
  );
};

export default Toolbar; 