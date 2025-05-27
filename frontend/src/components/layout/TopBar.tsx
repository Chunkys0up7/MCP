import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import SearchIcon from '@mui/icons-material/Search';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AccountCircle from '@mui/icons-material/AccountCircle';
import MenuIcon from '@mui/icons-material/Menu';
import useTheme from '@mui/material/styles/useTheme';
import useMediaQuery from '@mui/material/useMediaQuery';
import Tooltip from '@mui/material/Tooltip';

interface TopBarProps {
  onMenuClick?: () => void;
}

const iconButtonSx = {
  width: 44,
  height: 44,
  transition: 'background 0.2s, box-shadow 0.2s',
  '&:hover': { background: '#f3f6fa', boxShadow: 3 },
  '&:focus': { background: '#e3eefd', boxShadow: '0 0 0 3px #1976d2' },
};

const TopBar: React.FC<TopBarProps> = ({ onMenuClick }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  return (
    <AppBar position="static" color="default" elevation={1} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        {isMobile && (
          <Tooltip title="Open navigation menu" arrow>
            <IconButton
              color="inherit"
              aria-label="open navigation menu"
              edge="start"
              onClick={onMenuClick}
              sx={{ mr: 2, display: { md: 'none' }, ...iconButtonSx }}
            >
              <MenuIcon />
            </IconButton>
          </Tooltip>
        )}
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          AI Ops Console
        </Typography>
        <Tooltip title="Search" arrow>
          <IconButton color="inherit" aria-label="search" sx={iconButtonSx}>
            <SearchIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Notifications" arrow>
          <IconButton color="inherit" aria-label="notifications" sx={iconButtonSx}>
            <NotificationsIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Account" arrow>
          <IconButton color="inherit" aria-label="account" sx={iconButtonSx}>
            <AccountCircle />
          </IconButton>
        </Tooltip>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar; 