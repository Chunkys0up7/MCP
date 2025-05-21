import React from 'react';
import { Box, Drawer, useTheme, useMediaQuery } from '@mui/material';
import { useChainStore } from '../../infrastructure/state/chainStore';
import ChainCanvas from '../features/chain-builder/ChainCanvas';
import PropertiesPanel from '../features/node-config/PropertiesPanel';
import type { Node } from 'reactflow';
import type { NodeData } from '../../infrastructure/types/node';

const DRAWER_WIDTH = 320;

const WorkspaceLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { selectedNode, updateNode } = useChainStore();
  const [isDrawerOpen, setIsDrawerOpen] = React.useState(!isMobile);

  React.useEffect(() => {
    setIsDrawerOpen(!isMobile);
  }, [isMobile]);

  const handleNodeUpdate = (nodeId: string, data: Record<string, unknown>) => {
    updateNode(nodeId, data);
  };

  return (
    <Box sx={{ display: 'flex', height: '100%' }}>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: '100%',
          overflow: 'hidden',
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginRight: isDrawerOpen ? `${DRAWER_WIDTH}px` : 0,
        }}
      >
        <ChainCanvas />
      </Box>
      <Drawer
        variant={isMobile ? 'temporary' : 'persistent'}
        anchor="right"
        open={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            height: '100%',
            borderLeft: `1px solid ${theme.palette.divider}`,
          },
        }}
      >
        {selectedNode && (
          <PropertiesPanel
            node={selectedNode as Node<NodeData>}
            onUpdate={handleNodeUpdate}
          />
        )}
      </Drawer>
    </Box>
  );
};

export default WorkspaceLayout; 