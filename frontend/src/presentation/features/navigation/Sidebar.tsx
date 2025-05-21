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
import { designTokens } from '../../design-system/theme';

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
        return designTokens.colors.nodeTypes.llm;
      case 'notebook':
        return designTokens.colors.nodeTypes.notebook;
      case 'data':
        return designTokens.colors.nodeTypes.data;
      default:
        return '#666';
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
          >
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText primary="Dashboard" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/create-mcp'}
            onClick={() => handleNavigation('/create-mcp')}
            aria-label="Create MCP"
          >
            <ListItemIcon>
              <AddIcon />
            </ListItemIcon>
            <ListItemText primary="Create MCP" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/manage-mcps'}
            onClick={() => handleNavigation('/manage-mcps')}
            aria-label="Manage MCPs"
          >
            <ListItemIcon>
              <StorageIcon />
            </ListItemIcon>
            <ListItemText primary="Manage MCPs" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/test-mcps'}
            onClick={() => handleNavigation('/test-mcps')}
            aria-label="Test MCPs"
          >
            <ListItemIcon>
              <ScienceIcon />
            </ListItemIcon>
            <ListItemText primary="Test MCPs" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/chain-builder'}
            onClick={() => handleNavigation('/chain-builder')}
            aria-label="Chain Builder"
          >
            <ListItemIcon>
              <AccountTreeIcon />
            </ListItemIcon>
            <ListItemText primary="Chain Builder" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === '/settings'}
            onClick={() => handleNavigation('/settings')}
            aria-label="Settings"
          >
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItemButton>
        </ListItem>
      </List>

      <Divider />

      {/* MCP Library */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <ListItemButton onClick={handleMcpLibraryClick}>
          <ListItemText 
            primary="MCP Library" 
            primaryTypographyProps={{ fontWeight: 600 }}
          />
          {mcpLibraryOpen ? <ExpandLess /> : <ExpandMore />}
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
                    '&:hover': {
                      bgcolor: 'action.hover',
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