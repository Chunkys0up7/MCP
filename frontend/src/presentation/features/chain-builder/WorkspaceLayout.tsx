import React, { useState, useCallback } from 'react';
import { Box, IconButton, Paper, Drawer, useTheme, useMediaQuery } from '@mui/material';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
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
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Toolbar
        onSave={handleSaveChain}
        onExecute={handleExecuteChain}
        onToggleProperties={toggleProperties}
        onToggleLibrary={toggleLibrary}
        isLoading={isLoading}
      />
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
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
        >
          <MCPLibrary onAddMCP={handleAddMCP} />
        </Drawer>

        {/* Main Canvas */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ 
            flex: 1, 
            position: 'relative',
            height: '100%',
            minHeight: 0, // This is important for flexbox to work correctly
            '& .react-flow': {
              height: '100%',
              width: '100%'
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
              borderLeft: '1px solid',
              borderColor: 'divider',
            },
          }}
        >
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
            backgroundColor: 'background.paper',
            '&:hover': { backgroundColor: 'background.paper' },
          }}
        >
          {isConsoleCollapsed ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        </IconButton>
        <Paper
          sx={{
            height: isConsoleCollapsed ? 0 : CONSOLE_HEIGHT,
            transition: 'height 0.3s ease-in-out',
            overflow: 'hidden',
          }}
        >
          <ExecutionConsole />
        </Paper>
      </Box>
    </Box>
  );
};

export default WorkspaceLayout; 