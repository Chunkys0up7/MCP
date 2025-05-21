import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import PropertiesPanel from '../PropertiesPanel';
import '@testing-library/jest-dom';

describe('PropertiesPanel', () => {
  const mockNode = {
    id: 'node1',
    type: 'mcp',
    data: {
      label: 'Test Node',
      config: {
        model: 'gpt-4',
        temperature: 0.7,
      },
    },
  };

  const mockOnUpdateNode = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders node properties when a node is selected', () => {
    render(
      <PropertiesPanel
        selectedNode={mockNode}
        onUpdateNode={mockOnUpdateNode}
      />
    );

    expect(screen.getByText('Node Properties')).toBeInTheDocument();
    expect(screen.getByText('Test Node')).toBeInTheDocument();
    expect(screen.getByText('Model')).toBeInTheDocument();
    expect(screen.getByText('Temperature')).toBeInTheDocument();
  });

  it('shows empty state when no node is selected', () => {
    render(
      <PropertiesPanel
        selectedNode={null}
        onUpdateNode={mockOnUpdateNode}
      />
    );

    expect(screen.getByText(/select a node/i)).toBeInTheDocument();
  });

  it('updates node properties when form is changed', () => {
    render(
      <PropertiesPanel
        selectedNode={mockNode}
        onUpdateNode={mockOnUpdateNode}
      />
    );

    const modelInput = screen.getByLabelText(/model/i);
    fireEvent.change(modelInput, { target: { value: 'gpt-3.5-turbo' } });

    expect(mockOnUpdateNode).toHaveBeenCalledWith('node1', {
      config: {
        model: 'gpt-3.5-turbo',
        temperature: 0.7,
      },
    });
  });

  it('validates temperature input', () => {
    render(
      <PropertiesPanel
        selectedNode={mockNode}
        onUpdateNode={mockOnUpdateNode}
      />
    );

    const tempInput = screen.getByLabelText(/temperature/i);
    fireEvent.change(tempInput, { target: { value: '2' } });

    expect(screen.getByText(/temperature must be between 0 and 1/i)).toBeInTheDocument();
  });

  it('handles different node types', () => {
    const notebookNode = {
      id: 'node2',
      type: 'notebook',
      data: {
        label: 'Notebook Node',
        config: {
          path: '/path/to/notebook.ipynb',
        },
      },
    };

    render(
      <PropertiesPanel
        selectedNode={notebookNode}
        onUpdateNode={mockOnUpdateNode}
      />
    );

    expect(screen.getByText('Notebook Node')).toBeInTheDocument();
    expect(screen.getByText('Path')).toBeInTheDocument();
  });
}); 