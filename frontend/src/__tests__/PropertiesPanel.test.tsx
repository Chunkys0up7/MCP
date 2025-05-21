import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import PropertiesPanel from '../presentation/features/node-config/PropertiesPanel';
import { describe, it, expect } from 'vitest';

const mockNode = {
  id: '1',
  data: { label: 'Test Node', type: 'llm', config: {} },
  position: { x: 0, y: 0 },
};

describe('PropertiesPanel', () => {
  it('renders prompt when no node is selected', () => {
    render(<PropertiesPanel />);
    expect(screen.getByText(/select a node/i)).toBeInTheDocument();
  });

  it('renders node properties when node is selected', () => {
    render(<PropertiesPanel selectedNode={mockNode as any} />);
    expect(screen.getByText(/Node Properties/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Type/i)).toBeInTheDocument();
  });
}); 