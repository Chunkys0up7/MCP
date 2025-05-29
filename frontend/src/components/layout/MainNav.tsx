import React from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import DashboardIcon from '@mui/icons-material/Dashboard';
import StorefrontIcon from '@mui/icons-material/Storefront';
import BuildIcon from '@mui/icons-material/Build';
import TimelineIcon from '@mui/icons-material/Timeline';
import { useNavigate, useLocation } from 'react-router-dom';
import useTheme from '@mui/material/styles/useTheme';
import useMediaQuery from '@mui/material/useMediaQuery';

const navItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Marketplace', icon: <StorefrontIcon />, path: '/marketplace' },
  { text: 'Workflow Builder', icon: <BuildIcon />, path: '/workflow-builder' },
  { text: 'Execution Monitor', icon: <TimelineIcon />, path: '/execution-monitor' },
];

interface MainNavProps {
  mobileOpen: boolean;
  onDrawerToggle: () => void;
  drawerWidth?: number;
}

const MainNav: React.FC<MainNavProps> = ({ mobileOpen, onDrawerToggle, drawerWidth = 220 }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const drawerContent = (
    <List>
      {navItems.map((item) => (
        <ListItem
          button
          key={item.text}
          selected={location.pathname === item.path}
          onClick={() => navigate(item.path)}
        >
          <ListItemIcon>{item.icon}</ListItemIcon>
          <ListItemText primary={item.text} />
        </ListItem>
      ))}
    </List>
  );

  return (
    <>
      {/* Temporary drawer for mobile */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { width: drawerWidth },
        }}
        role="navigation"
        aria-label="Main Navigation Drawer"
      >
        {drawerContent}
      </Drawer>
      {/* Permanent drawer for desktop */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
        open
        role="navigation"
        aria-label="Main Navigation Sidebar"
      >
        {drawerContent}
      </Drawer>
    </>
  );
};

export default MainNav; 