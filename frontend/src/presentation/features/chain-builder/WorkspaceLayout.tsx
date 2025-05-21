import React from 'react';
import { Box, Drawer, Typography } from '@mui/material';
import { useChainStore } from '../../../infrastructure/state/chainStore';
import { useNotification } from '../../../infrastructure/context/NotificationContext';
import MCPLibrary from './MCPLibrary';
import WorkflowDesign from './WorkflowDesign';
import PropertiesPanel from './PropertiesPanel';
import { MCPItem } from '../../../infrastructure/types/node';
import type { Node, NodeChange, EdgeChange } from 'reactflow';

const drawerWidth = 240;

export const WorkspaceLayout: React.FC = () => {
  const { nodes, edges, addNode, removeNode, removeEdge, updateNode, setSelectedNode, selectedNode } = useChainStore();
  const { showSuccess } = useNotification();

  const handleAddMCP = (item: MCPItem) => {
    addNode({
      id: `${item.type}-${Date.now()}`,
      type: item.type,
      position: { x: 100, y: 100 },
      data: { ...item },
    });
    showSuccess('Node added successfully');
  };

  const handleNodeDelete = (nodeId: string) => {
    removeNode(nodeId);
    showSuccess('Node deleted successfully');
  };

  const handleEdgeDelete = (edgeId: string) => {
    removeEdge(edgeId);
    showSuccess('Edge deleted successfully');
  };

  const handleNodeSelect = (node: Node | null) => {
    setSelectedNode(node);
  };

  const handleNodeUpdate = (nodeId: string, data: Record<string, unknown>) => {
    updateNode(nodeId, data);
    showSuccess('Node updated successfully');
  };

  const handleNodesChange = (changes: NodeChange[]) => {
    // Handle node changes
  };

  const handleEdgesChange = (changes: EdgeChange[]) => {
    // Handle edge changes
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            MCP Library
          </Typography>
          <MCPLibrary onAddMCP={handleAddMCP} />
        </Box>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <WorkflowDesign
          nodes={nodes}
          edges={edges}
          onNodeDelete={handleNodeDelete}
          onEdgeDelete={handleEdgeDelete}
          onNodeSelect={handleNodeSelect}
          onNodesChange={handleNodesChange}
          onEdgesChange={handleEdgesChange}
        />
      </Box>
      <Drawer
        variant="permanent"
        anchor="right"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Properties
          </Typography>
          {selectedNode && (
            <PropertiesPanel
              node={selectedNode}
              onUpdate={handleNodeUpdate}
            />
          )}
        </Box>
      </Drawer>
    </Box>
  );
}; 