import { render, screen, fireEvent } from '@testing-library/react';
import Toolbar from '../presentation/features/chain-builder/Toolbar';
import { describe, it, expect, vi } from 'vitest';
import * as chainStore from '../infrastructure/state/chainStore';

describe('Toolbar', () => {
  it('renders all action buttons', () => {
    render(<Toolbar />);
    expect(screen.getByTitle('Save')).toBeInTheDocument();
    expect(screen.getByTitle('Load')).toBeInTheDocument();
    expect(screen.getByTitle('Export')).toBeInTheDocument();
    expect(screen.getByTitle('Undo')).toBeInTheDocument();
    expect(screen.getByTitle('Redo')).toBeInTheDocument();
  });

  it('calls undo and redo actions', () => {
    const undo = vi.fn();
    const redo = vi.fn();
    vi.spyOn(chainStore, 'useChainStore').mockReturnValue({ undo, redo, nodes: [], edges: [] } as any);
    render(<Toolbar />);
    fireEvent.click(screen.getByTitle('Undo'));
    fireEvent.click(screen.getByTitle('Redo'));
    expect(undo).toHaveBeenCalled();
    expect(redo).toHaveBeenCalled();
  });
}); 