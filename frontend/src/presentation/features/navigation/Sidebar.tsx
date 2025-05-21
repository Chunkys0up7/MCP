import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Paper,
  Collapse,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AddIcon from '@mui/icons-material/Add';
import StorageIcon from '@mui/icons-material/Storage';
import ScienceIcon from '@mui/icons-material/Science';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import SettingsIcon from '@mui/icons-material/Settings';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';

interface MCPItem {
  id: string;
  name: string;
  type: 'llm' | 'notebook' | 'data';
  description: string;
}

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [mcpLibraryOpen, setMcpLibraryOpen] = React.useState(true);
  const [mcps, setMcps] = React.useState<MCPItem[]>([]);

  // TODO: Replace with actual API call
  React.useEffect(() => {
    // Mock data for now
    setMcps([
      {
        id: '1',
        name: 'GPT-4 Prompt',
        type: 'llm',
        description: 'Advanced language model for complex tasks',
      },
      {
        id: '2',
        name: 'Data Analysis',
        type: 'notebook',
        description: 'Jupyter notebook for data processing',
      },
      {
        id: '3',
        name: 'CSV Loader',
        type: 'data',
        description: 'Load and process CSV files',
      },
    ]);
  }, []);

  const handleMcpLibraryClick = () => {
    setMcpLibraryOpen(!mcpLibraryOpen);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const getMcpTypeColor = (type: MCPItem['type']) => {
    switch (type) {
      case 'llm':
        return '#0b79ee';
      case 'notebook':
        return '#00bcd4';
      case 'data':
        return '#4caf50';
      default:
        return '#314c68';
    }
  };

  return (
    <Box
      sx={{
        width: 280,
        height: '100vh',
        borderRight: 1,
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
      }}
      role="navigation"
      aria-label="Main Navigation"
    >
      {/* Navigation Items */}
      <List sx={{ pt: 2 }}>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/'}
            onClick={() => handleNavigation('/')}
            aria-label="Dashboard"
            sx={{
              '&.Mui-selected': {
                bgcolor: 'rgba(11, 121, 238, 0.1)',
                '&:hover': {
                  bgcolor: 'rgba(11, 121, 238, 0.15)',
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: 'text.primary' }}>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Dashboard" 
              primaryTypographyProps={{ 
                fontWeight: location.pathname === '/' ? 700 : 400,
                color: 'text.primary'
              }}
            />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/create-mcp'}
            onClick={() => handleNavigation('/create-mcp')}
            aria-label="Create MCP"
            sx={{
              '&.Mui-selected': {
                bgcolor: 'rgba(11, 121, 238, 0.1)',
                '&:hover': {
                  bgcolor: 'rgba(11, 121, 238, 0.15)',
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: 'text.primary' }}>
              <AddIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Create MCP" 
              primaryTypographyProps={{ 
                fontWeight: location.pathname === '/create-mcp' ? 700 : 400,
                color: 'text.primary'
              }}
            />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/manage-mcps'}
            onClick={() => handleNavigation('/manage-mcps')}
            aria-label="Manage MCPs"
            sx={{
              '&.Mui-selected': {
                bgcolor: 'rgba(11, 121, 238, 0.1)',
                '&:hover': {
                  bgcolor: 'rgba(11, 121, 238, 0.15)',
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: 'text.primary' }}>
              <StorageIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Manage MCPs" 
              primaryTypographyProps={{ 
                fontWeight: location.pathname === '/manage-mcps' ? 700 : 400,
                color: 'text.primary'
              }}
            />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/test-mcps'}
            onClick={() => handleNavigation('/test-mcps')}
            aria-label="Test MCPs"
            sx={{
              '&.Mui-selected': {
                bgcolor: 'rgba(11, 121, 238, 0.1)',
                '&:hover': {
                  bgcolor: 'rgba(11, 121, 238, 0.15)',
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: 'text.primary' }}>
              <ScienceIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Test MCPs" 
              primaryTypographyProps={{ 
                fontWeight: location.pathname === '/test-mcps' ? 700 : 400,
                color: 'text.primary'
              }}
            />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/chain-builder'}
            onClick={() => handleNavigation('/chain-builder')}
            aria-label="Chain Builder"
            sx={{
              '&.Mui-selected': {
                bgcolor: 'rgba(11, 121, 238, 0.1)',
                '&:hover': {
                  bgcolor: 'rgba(11, 121, 238, 0.15)',
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: 'text.primary' }}>
              <AccountTreeIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Chain Builder" 
              primaryTypographyProps={{ 
                fontWeight: location.pathname === '/chain-builder' ? 700 : 400,
                color: 'text.primary'
              }}
            />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/settings'}
            onClick={() => handleNavigation('/settings')}
            aria-label="Settings"
            sx={{
              '&.Mui-selected': {
                bgcolor: 'rgba(11, 121, 238, 0.1)',
                '&:hover': {
                  bgcolor: 'rgba(11, 121, 238, 0.15)',
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: 'text.primary' }}>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Settings" 
              primaryTypographyProps={{ 
                fontWeight: location.pathname === '/settings' ? 700 : 400,
                color: 'text.primary'
              }}
            />
          </ListItemButton>
        </ListItem>
      </List>

      <Divider />

      {/* MCP Library */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <ListItemButton 
          onClick={handleMcpLibraryClick}
          sx={{
            '&:hover': {
              bgcolor: 'rgba(11, 121, 238, 0.05)',
            },
          }}
        >
          <ListItemText 
            primary="MCP Library" 
            primaryTypographyProps={{ 
              fontWeight: 600,
              color: 'text.primary'
            }}
          />
          {mcpLibraryOpen ? <ExpandLess sx={{ color: 'text.primary' }} /> : <ExpandMore sx={{ color: 'text.primary' }} />}
        </ListItemButton>
        <Collapse in={mcpLibraryOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {mcps.map((mcp) => (
              <ListItem key={mcp.id} disablePadding>
                <Paper
                  sx={{
                    m: 1,
                    p: 1,
                    width: '100%',
                    cursor: 'pointer',
                    bgcolor: 'background.default',
                    border: '1px solid',
                    borderColor: 'divider',
                    '&:hover': {
                      bgcolor: 'rgba(11, 121, 238, 0.05)',
                      borderColor: 'primary.main',
                    },
                  }}
                  elevation={0}
                  onClick={() => {
                    // TODO: Implement drag and drop to canvas
                    console.log('Add MCP to canvas:', mcp);
                  }}
                >
                  <Typography variant="subtitle2" sx={{ color: getMcpTypeColor(mcp.type) }}>
                    {mcp.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {mcp.type.toUpperCase()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                    {mcp.description}
                  </Typography>
                </Paper>
              </ListItem>
            ))}
          </List>
        </Collapse>
      </Box>
    </Box>
  );
};

export default Sidebar; 