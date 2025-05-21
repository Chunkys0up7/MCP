import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import MCPLibrary from '../MCPLibrary';
import '@testing-library/jest-dom';

describe('MCPLibrary', () => {
  const mockMCPs = [
    {
      id: 'llm-1',
      name: 'GPT-4',
      type: 'llm' as const,
      description: 'OpenAI GPT-4 model',
    },
    {
      id: 'notebook-1',
      name: 'Data Analysis',
      type: 'notebook' as const,
      description: 'Jupyter notebook for data analysis',
    },
  ];

  const mockOnAddMCP = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders MCP list', () => {
    render(<MCPLibrary onAddMCP={mockOnAddMCP} />);

    expect(screen.getByText('GPT-4')).toBeInTheDocument();
    expect(screen.getByText('Data Analysis')).toBeInTheDocument();
    expect(screen.getByText('OpenAI GPT-4 model')).toBeInTheDocument();
    expect(screen.getByText('Jupyter notebook for data analysis')).toBeInTheDocument();
  });

  it('calls onAddMCP when an MCP is clicked', () => {
    render(<MCPLibrary onAddMCP={mockOnAddMCP} />);

    const addButtons = screen.getAllByText('Add to Chain');
    fireEvent.click(addButtons[0]);
    expect(mockOnAddMCP).toHaveBeenCalledWith(expect.objectContaining({
      id: 'llm-1',
      name: 'GPT-4',
      type: 'llm',
    }));
  });

  it('shows help tooltip', () => {
    render(<MCPLibrary onAddMCP={mockOnAddMCP} />);

    const helpButtons = screen.getAllByRole('button', { name: /learn more/i });
    expect(helpButtons).toHaveLength(2);
  });

  it('supports drag and drop', () => {
    render(<MCPLibrary onAddMCP={mockOnAddMCP} />);

    const cards = screen.getAllByRole('button', { name: /add to chain/i });
    const dragEvent = {
      dataTransfer: {
        setData: jest.fn(),
      },
    };

    fireEvent.dragStart(cards[0], dragEvent);
    expect(dragEvent.dataTransfer.setData).toHaveBeenCalledWith(
      'application/json',
      expect.stringContaining('GPT-4')
    );
  });
}); 