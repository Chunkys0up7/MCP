import React, { useState, useCallback } from 'react';
import { Box, IconButton, Paper, Drawer, useTheme, useMediaQuery, Typography, Button } from '@mui/material';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Toolbar from './Toolbar';
import PropertiesPanel from '../node-config/PropertiesPanel';
import ExecutionConsole from '../execution-monitor/ExecutionConsole';
import ChainInfo from './ChainInfo';
import ChainConfig from './ChainConfig';
import MCPLibrary from './MCPLibrary';
import WorkflowDesign from './WorkflowDesign';
import { useChainOperations } from '../../../infrastructure/hooks/useChainOperations';
import { useChainStore } from '../../../infrastructure/state/chainStore';
import type { Node } from 'reactflow';
import type { MCPItem } from '../../../infrastructure/types/node';

const DRAWER_WIDTH = 300;
const CONSOLE_HEIGHT = 200;

const WorkspaceLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [isConsoleCollapsed, setIsConsoleCollapsed] = useState(false);
  const [isPropertiesOpen, setIsPropertiesOpen] = useState(!isMobile);
  const [isLibraryOpen, setIsLibraryOpen] = useState(!isMobile);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const { chainInfo, chainConfig } = useChainStore();

  const {
    nodes,
    edges,
    isLoading,
    handleLoadChain,
    handleSaveChain,
    handleExecuteChain,
    handleAddMCP,
    handleUpdateNode,
    handleAddEdge,
    handleRemoveNode,
    handleRemoveEdge,
  } = useChainOperations();

  const toggleConsole = useCallback(() => {
    setIsConsoleCollapsed(prev => !prev);
  }, []);

  const toggleProperties = useCallback(() => {
    setIsPropertiesOpen(prev => !prev);
  }, []);

  const toggleLibrary = useCallback(() => {
    setIsLibraryOpen(prev => !prev);
  }, []);

  const handleNodeSelect = useCallback((node: Node | null) => {
    setSelectedNode(node);
    if (node && isMobile) {
      setIsPropertiesOpen(true);
    }
  }, [isMobile]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', bgcolor: 'background.default' }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        bgcolor: 'background.default', 
        p: 2, 
        pb: 1,
        borderBottom: 1,
        borderColor: 'divider'
      }}>
        <IconButton 
          sx={{ 
            color: 'text.primary',
            mr: 2
          }}
        >
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h2" sx={{ flex: 1, textAlign: 'center', pr: 6 }}>
          Chain Builder
        </Typography>
      </Box>

      {/* Main Content */}
      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* MCP Library Drawer */}
        <Drawer
          variant={isMobile ? 'temporary' : 'persistent'}
          open={isLibraryOpen}
          onClose={toggleLibrary}
          sx={{
            width: DRAWER_WIDTH,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: DRAWER_WIDTH,
              boxSizing: 'border-box',
              borderRight: 1,
              borderColor: 'divider',
            },
          }}
        >
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h3">
              MCP Library
            </Typography>
          </Box>
          <MCPLibrary onAddMCP={handleAddMCP} />
        </Drawer>

        {/* Main Canvas */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
          <Box sx={{ 
            flex: 1, 
            position: 'relative',
            height: '100%',
            minHeight: 0,
            '& .react-flow': {
              height: '100%',
              width: '100%',
              bgcolor: 'background.default',
            }
          }}>
            <WorkflowDesign
              nodes={nodes}
              edges={edges}
              onNodesChange={handleUpdateNode}
              onEdgesChange={handleAddEdge}
              onNodeDelete={handleRemoveNode}
              onEdgeDelete={handleRemoveEdge}
              onNodeSelect={handleNodeSelect}
            />
          </Box>
        </Box>

        {/* Properties Panel Drawer */}
        <Drawer
          variant={isMobile ? 'temporary' : 'persistent'}
          anchor="right"
          open={isPropertiesOpen}
          onClose={toggleProperties}
          sx={{
            width: DRAWER_WIDTH,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: DRAWER_WIDTH,
              boxSizing: 'border-box',
              borderLeft: 1,
              borderColor: 'divider',
            },
          }}
        >
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h3">
              {selectedNode ? 'Node Properties' : 'Chain Properties'}
            </Typography>
          </Box>
          {selectedNode ? (
            <PropertiesPanel node={selectedNode} />
          ) : (
            <Box sx={{ p: 2 }}>
              <ChainInfo />
              {chainInfo && chainConfig && (
                <ChainConfig nodeId={chainInfo.id} config={chainConfig} />
              )}
            </Box>
          )}
        </Drawer>
      </Box>

      {/* Execution Console */}
      <Box sx={{ position: 'relative' }}>
        <IconButton
          onClick={toggleConsole}
          sx={{
            position: 'absolute',
            top: -20,
            right: 20,
            bgcolor: 'background.paper',
            border: 1,
            borderColor: 'divider',
            '&:hover': { bgcolor: 'background.paper' },
          }}
        >
          {isConsoleCollapsed ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        </IconButton>
        <Paper
          sx={{
            height: isConsoleCollapsed ? 0 : CONSOLE_HEIGHT,
            transition: 'height 0.3s ease-in-out',
            overflow: 'hidden',
            borderTop: 1,
            borderColor: 'divider',
          }}
        >
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h3">
              Execution Console
            </Typography>
          </Box>
          <ExecutionConsole />
        </Paper>
      </Box>
    </Box>
  );
};

export default WorkspaceLayout; 