import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Toolbar from '../Toolbar';
import '@testing-library/jest-dom';

describe('Toolbar', () => {
  const mockHandlers = {
    onSave: jest.fn(),
    onExecute: jest.fn(),
    onStop: jest.fn(),
    onUndo: jest.fn(),
    onRedo: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all buttons when all handlers are provided', () => {
    render(
      <Toolbar
        onSave={mockHandlers.onSave}
        onExecute={mockHandlers.onExecute}
        onStop={mockHandlers.onStop}
        onUndo={mockHandlers.onUndo}
        onRedo={mockHandlers.onRedo}
        isLoading={false}
        isExecuting={false}
        canUndo={true}
        canRedo={true}
      />
    );

    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /execute/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /stop/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /undo/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /redo/i })).toBeInTheDocument();
  });

  it('disables buttons when loading', () => {
    render(
      <Toolbar
        onSave={mockHandlers.onSave}
        onExecute={mockHandlers.onExecute}
        onStop={mockHandlers.onStop}
        onUndo={mockHandlers.onUndo}
        onRedo={mockHandlers.onRedo}
        isLoading={true}
        isExecuting={true}
        canUndo={true}
        canRedo={true}
      />
    );

    expect(screen.getByRole('button', { name: /save/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /execute/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /undo/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /redo/i })).toBeDisabled();
  });

  it('disables undo/redo buttons when not available', () => {
    render(
      <Toolbar
        onSave={mockHandlers.onSave}
        onExecute={mockHandlers.onExecute}
        onStop={mockHandlers.onStop}
        onUndo={mockHandlers.onUndo}
        onRedo={mockHandlers.onRedo}
        isLoading={false}
        isExecuting={false}
        canUndo={false}
        canRedo={false}
      />
    );

    expect(screen.getByRole('button', { name: /undo/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /redo/i })).toBeDisabled();
  });

  it('calls handlers when buttons are clicked', () => {
    render(
      <Toolbar
        onSave={mockHandlers.onSave}
        onExecute={mockHandlers.onExecute}
        onStop={mockHandlers.onStop}
        onUndo={mockHandlers.onUndo}
        onRedo={mockHandlers.onRedo}
        isLoading={false}
        isExecuting={false}
        canUndo={true}
        canRedo={true}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /save/i }));
    expect(mockHandlers.onSave).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /execute/i }));
    expect(mockHandlers.onExecute).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /stop/i }));
    expect(mockHandlers.onStop).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /undo/i }));
    expect(mockHandlers.onUndo).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /redo/i }));
    expect(mockHandlers.onRedo).toHaveBeenCalled();
  });

  it('shows loading spinner when saving', () => {
    render(
      <Toolbar
        onSave={mockHandlers.onSave}
        onExecute={mockHandlers.onExecute}
        onStop={mockHandlers.onStop}
        onUndo={mockHandlers.onUndo}
        onRedo={mockHandlers.onRedo}
        isLoading={true}
        isExecuting={false}
        canUndo={true}
        canRedo={true}
      />
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
}); 