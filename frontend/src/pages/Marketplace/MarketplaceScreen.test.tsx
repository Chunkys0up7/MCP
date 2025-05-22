import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import MarketplaceScreen from './MarketplaceScreen';

// Mock console.log for search submit
console.log = jest.fn();

describe('MarketplaceScreen', () => {
  beforeEach(() => {
    (console.log as jest.Mock).mockClear();
  });

  it('renders the main title and filter sections', () => {
    render(<MarketplaceScreen />);
    expect(screen.getByText('Component Marketplace')).toBeInTheDocument();
    expect(screen.getByLabelText('Search Components')).toBeInTheDocument();
    expect(screen.getByLabelText('Type')).toBeInTheDocument();
    expect(screen.getByLabelText('Compliance')).toBeInTheDocument();
    expect(screen.getByLabelText('Cost')).toBeInTheDocument();
  });

  it('renders initial mock components', () => {
    render(<MarketplaceScreen />);
    // Based on mockComponents in MarketplaceScreen.tsx
    expect(screen.getByText('Sentiment Analyzer')).toBeInTheDocument();
    expect(screen.getByText('Data Validator')).toBeInTheDocument();
    expect(screen.getByText('Image Classifier')).toBeInTheDocument();
    expect(screen.getByText('Notification Service')).toBeInTheDocument();
    expect(screen.getByText('Available Components (4)')).toBeInTheDocument();
  });

  it('filters components by type when type filter is changed', () => {
    render(<MarketplaceScreen />);
    const typeFilter = screen.getByLabelText('Type');

    fireEvent.change(typeFilter, { target: { value: 'AI Model' } });

    expect(screen.getByText('Sentiment Analyzer')).toBeInTheDocument();
    expect(screen.getByText('Image Classifier')).toBeInTheDocument();
    expect(screen.queryByText('Data Validator')).not.toBeInTheDocument();
    expect(screen.queryByText('Notification Service')).not.toBeInTheDocument();
    expect(screen.getByText('Available Components (2)')).toBeInTheDocument();
  });

  it('filters components by compliance when compliance filter is changed', () => {
    render(<MarketplaceScreen />);
    const complianceFilter = screen.getByLabelText('Compliance');

    fireEvent.change(complianceFilter, { target: { value: 'GDPR' } });

    expect(screen.getByText('Data Validator')).toBeInTheDocument();
    expect(screen.queryByText('Sentiment Analyzer')).not.toBeInTheDocument();
    expect(screen.getByText('Available Components (1)')).toBeInTheDocument();
  });
  
  it('filters components by search term in name', () => {
    render(<MarketplaceScreen />);
    const searchInput = screen.getByPlaceholderText('Search by name or description...');

    fireEvent.change(searchInput, { target: { value: 'Sentiment' } });
    // The filtering is live, so no need to click submit for this test case
    // but we can test submit if needed

    expect(screen.getByText('Sentiment Analyzer')).toBeInTheDocument();
    expect(screen.queryByText('Data Validator')).not.toBeInTheDocument();
    expect(screen.getByText('Available Components (1)')).toBeInTheDocument();
  });

  it('filters components by search term in description', () => {
    render(<MarketplaceScreen />);
    const searchInput = screen.getByPlaceholderText('Search by name or description...');

    fireEvent.change(searchInput, { target: { value: 'schemas' } });

    expect(screen.getByText('Data Validator')).toBeInTheDocument();
    expect(screen.queryByText('Sentiment Analyzer')).not.toBeInTheDocument();
    expect(screen.getByText('Available Components (1)')).toBeInTheDocument();
  });

  it('shows no components if search term matches nothing', () => {
    render(<MarketplaceScreen />);
    const searchInput = screen.getByPlaceholderText('Search by name or description...');

    fireEvent.change(searchInput, { target: { value: 'NonExistentTerm123' } });

    expect(screen.queryByText('Sentiment Analyzer')).not.toBeInTheDocument();
    expect(screen.getByText('No components match your current filters. Try adjusting your search criteria.')).toBeInTheDocument();
    expect(screen.getByText('Available Components (0)')).toBeInTheDocument();
  });

  it('combines type filter and search term', () => {
    render(<MarketplaceScreen />);
    const typeFilter = screen.getByLabelText('Type');
    const searchInput = screen.getByPlaceholderText('Search by name or description...');

    fireEvent.change(typeFilter, { target: { value: 'AI Model' } });
    fireEvent.change(searchInput, { target: { value: 'Image' } });

    expect(screen.getByText('Image Classifier')).toBeInTheDocument();
    expect(screen.queryByText('Sentiment Analyzer')).not.toBeInTheDocument(); 
    expect(screen.getByText('Available Components (1)')).toBeInTheDocument();
  });
  
  it('logs search term on form submit', () => {
    render(<MarketplaceScreen />);
    const searchInput = screen.getByPlaceholderText('Search by name or description...');
    const goButton = screen.getByRole('button', {name: 'Go'});

    fireEvent.change(searchInput, { target: { value: 'test search submit' } });
    fireEvent.click(goButton); // or fireEvent.submit on the form element if accessible

    expect(console.log).toHaveBeenCalledWith('Search submitted:', 'test search submit');
  });

  // Test for the cost filter is omitted because the actual filtering logic for cost isn't implemented in MarketplaceScreen.tsx
  // Once cost filtering logic is in place, tests for it should be added.
}); 