import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import QuickAccessToolbar from './QuickAccessToolbar';

// Mock alert for Create New button
global.alert = jest.fn();
// Mock console.log for search
console.log = jest.fn();

describe('QuickAccessToolbar', () => {
  beforeEach(() => {
    // Clear mock history before each test
    (global.alert as jest.Mock).mockClear();
    (console.log as jest.Mock).mockClear();
  });

  it('renders the Create New button and Global Search input', () => {
    render(<QuickAccessToolbar />);
    expect(screen.getByText('Create New Workflow')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Global Search...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
  });

  it('calls alert when Create New button is clicked and no callback is provided', () => {
    render(<QuickAccessToolbar />);
    fireEvent.click(screen.getByText('Create New Workflow'));
    expect(global.alert).toHaveBeenCalledWith('Create New clicked! Placeholder for template selection.');
  });

  it('calls onCreateNew callback when Create New button is clicked', () => {
    const mockOnCreateNew = jest.fn();
    render(<QuickAccessToolbar onCreateNew={mockOnCreateNew} />);
    fireEvent.click(screen.getByText('Create New Workflow'));
    expect(mockOnCreateNew).toHaveBeenCalledTimes(1);
    expect(global.alert).not.toHaveBeenCalled();
  });

  it('updates search term on input change', () => {
    render(<QuickAccessToolbar />);
    const searchInput = screen.getByPlaceholderText('Global Search...') as HTMLInputElement;
    fireEvent.change(searchInput, { target: { value: 'test search' } });
    expect(searchInput.value).toBe('test search');
  });

  it('calls console.log on search submit when no callback is provided', () => {
    render(<QuickAccessToolbar />);
    const searchInput = screen.getByPlaceholderText('Global Search...');
    const searchButton = screen.getByRole('button', { name: 'Search' });

    fireEvent.change(searchInput, { target: { value: 'my query' } });
    fireEvent.click(searchButton);

    expect(console.log).toHaveBeenCalledWith('Search submitted: my query');
  });

  it('calls onSearch callback with the search term on submit', () => {
    const mockOnSearch = jest.fn();
    render(<QuickAccessToolbar onSearch={mockOnSearch} />);
    const searchInput = screen.getByPlaceholderText('Global Search...');
    const searchButton = screen.getByRole('button', { name: 'Search' });

    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.click(searchButton); // Or fireEvent.submit(form)

    expect(mockOnSearch).toHaveBeenCalledWith('test query');
    expect(console.log).not.toHaveBeenCalled();
  });
}); 