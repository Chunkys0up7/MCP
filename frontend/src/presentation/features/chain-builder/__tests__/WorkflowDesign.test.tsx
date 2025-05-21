import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import WorkflowDesign from '../WorkflowDesign';
import type { Node, Edge } from 'reactflow';
import '@testing-library/jest-dom';

// Mock ReactFlow components
jest.mock('reactflow', () => ({
  ReactFlow: ({ children, nodes, edges, onNodesChange, onEdgesChange, onConnect }: any) => (
    <div data-testid="react-flow">
      <div data-testid="nodes">{JSON.stringify(nodes)}</div>
      <div data-testid="edges">{JSON.stringify(edges)}</div>
      <button
        data-testid="add-node"
        onClick={() =>
          onNodesChange([
            {
              type: 'add',
              item: { id: 'new-node', type: 'mcp', position: { x: 0, y: 0 }, data: {} },
            },
          ])
        }
      >
        Add Node
      </button>
      <button
        data-testid="add-edge"
        onClick={() =>
          onEdgesChange([
            {
              type: 'add',
              item: { id: 'new-edge', source: 'node1', target: 'node2' },
            },
          ])
        }
      >
        Add Edge
      </button>
      <button
        data-testid="connect-nodes"
        onClick={() =>
          onConnect({
            source: 'node1',
            target: 'node2',
            sourceHandle: null,
            targetHandle: null,
          })
        }
      >
        Connect Nodes
      </button>
    </div>
  ),
  Background: () => <div data-testid="background" />,
  Controls: () => <div data-testid="controls" />,
  MiniMap: () => <div data-testid="minimap" />,
}));

describe('WorkflowDesign', () => {
  const mockNodes: Node[] = [
    {
      id: 'node1',
      type: 'mcp',
      position: { x: 0, y: 0 },
      data: { label: 'Node 1' },
    },
  ];

  const mockEdges: Edge[] = [
    {
      id: 'edge1',
      source: 'node1',
      target: 'node2',
    },
  ];

  const mockHandlers = {
    onNodesChange: jest.fn(),
    onEdgesChange: jest.fn(),
    onConnect: jest.fn(),
    onNodeDelete: jest.fn(),
    onEdgeDelete: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with initial nodes and edges', () => {
    render(
      <WorkflowDesign
        nodes={mockNodes}
        edges={mockEdges}
        onNodesChange={mockHandlers.onNodesChange}
        onEdgesChange={mockHandlers.onEdgesChange}
        onConnect={mockHandlers.onConnect}
        onNodeDelete={mockHandlers.onNodeDelete}
        onEdgeDelete={mockHandlers.onEdgeDelete}
      />
    );

    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
    expect(screen.getByTestId('background')).toBeInTheDocument();
    expect(screen.getByTestId('controls')).toBeInTheDocument();
    expect(screen.getByTestId('minimap')).toBeInTheDocument();
  });

  it('handles node changes', () => {
    render(
      <WorkflowDesign
        nodes={mockNodes}
        edges={mockEdges}
        onNodesChange={mockHandlers.onNodesChange}
        onEdgesChange={mockHandlers.onEdgesChange}
        onConnect={mockHandlers.onConnect}
        onNodeDelete={mockHandlers.onNodeDelete}
        onEdgeDelete={mockHandlers.onEdgeDelete}
      />
    );

    fireEvent.click(screen.getByTestId('add-node'));
    expect(mockHandlers.onNodesChange).toHaveBeenCalled();
  });

  it('handles edge changes', () => {
    render(
      <WorkflowDesign
        nodes={mockNodes}
        edges={mockEdges}
        onNodesChange={mockHandlers.onNodesChange}
        onEdgesChange={mockHandlers.onEdgesChange}
        onConnect={mockHandlers.onConnect}
        onNodeDelete={mockHandlers.onNodeDelete}
        onEdgeDelete={mockHandlers.onEdgeDelete}
      />
    );

    fireEvent.click(screen.getByTestId('add-edge'));
    expect(mockHandlers.onEdgesChange).toHaveBeenCalled();
  });

  it('handles node connections', () => {
    render(
      <WorkflowDesign
        nodes={mockNodes}
        edges={mockEdges}
        onNodesChange={mockHandlers.onNodesChange}
        onEdgesChange={mockHandlers.onEdgesChange}
        onConnect={mockHandlers.onConnect}
        onNodeDelete={mockHandlers.onNodeDelete}
        onEdgeDelete={mockHandlers.onEdgeDelete}
      />
    );

    fireEvent.click(screen.getByTestId('connect-nodes'));
    expect(mockHandlers.onConnect).toHaveBeenCalled();
  });
}); 