import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FacetedSearchScreen from './FacetedSearchScreen';
import { componentRegistryService } from '../../services/componentRegistryService';

// Mock the component registry service
jest.mock('../../services/componentRegistryService', () => ({
  componentRegistryService: {
    searchComponents: jest.fn(),
    getAvailableTypes: jest.fn(),
    getPopularTags: jest.fn(),
  },
}));

describe('FacetedSearchScreen', () => {
  const mockComponents = [
    {
      id: '1',
      name: 'Test Component',
      description: 'Test Description',
      type: 'type1',
      tags: ['tag1', 'tag2'],
      rating: 4.5,
      usageCount: 100,
      author: 'Test Author',
      lastUpdated: '2024-03-24T12:00:00Z',
      version: '1.0.0',
      documentation: 'Test Documentation',
      dependencies: [],
    },
  ];

  const mockSearchResponse = {
    components: mockComponents,
    total: 1,
    page: 1,
    pageSize: 10,
    facets: {
      types: { type1: 1 },
      tags: { tag1: 1, tag2: 1 },
    },
  };

  const mockTypes = ['type1', 'type2'];
  const mockTags = ['tag1', 'tag2', 'tag3'];

  beforeEach(() => {
    jest.clearAllMocks();
    (componentRegistryService.searchComponents as jest.Mock).mockResolvedValue(mockSearchResponse);
    (componentRegistryService.getAvailableTypes as jest.Mock).mockResolvedValue(mockTypes);
    (componentRegistryService.getPopularTags as jest.Mock).mockResolvedValue(mockTags);
  });

  it('shows loading state initially', () => {
    render(<FacetedSearchScreen />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays components after loading', async () => {
    render(<FacetedSearchScreen />);

    await waitFor(() => {
      expect(screen.getByText('Test Component')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
      expect(screen.getByText('tag1')).toBeInTheDocument();
      expect(screen.getByText('tag2')).toBeInTheDocument();
      expect(screen.getByText('4.5')).toBeInTheDocument();
      expect(screen.getByText('100 uses')).toBeInTheDocument();
    });
  });

  it('handles search input', async () => {
    render(<FacetedSearchScreen />);

    const searchInput = screen.getByPlaceholderText('Search components...');
    fireEvent.change(searchInput, { target: { value: 'test' } });

    // Wait for debounce
    await waitFor(() => {
      expect(componentRegistryService.searchComponents).toHaveBeenCalledWith(
        expect.objectContaining({ searchTerm: 'test' }),
        1,
        10
      );
    });
  });

  it('handles type filter selection', async () => {
    render(<FacetedSearchScreen />);

    await waitFor(() => {
      expect(screen.getByText('type1')).toBeInTheDocument();
    });

    const typeCheckbox = screen.getByLabelText('type1');
    fireEvent.click(typeCheckbox);

    await waitFor(() => {
      expect(componentRegistryService.searchComponents).toHaveBeenCalledWith(
        expect.objectContaining({ type: ['type1'] }),
        1,
        10
      );
    });
  });

  it('handles tag filter selection', async () => {
    render(<FacetedSearchScreen />);

    await waitFor(() => {
      expect(screen.getByText('tag1')).toBeInTheDocument();
    });

    const tagButton = screen.getByText('tag1');
    fireEvent.click(tagButton);

    await waitFor(() => {
      expect(componentRegistryService.searchComponents).toHaveBeenCalledWith(
        expect.objectContaining({ tags: ['tag1'] }),
        1,
        10
      );
    });
  });

  it('handles rating filter', async () => {
    render(<FacetedSearchScreen />);

    const ratingInput = screen.getByLabelText('Minimum Rating');
    fireEvent.change(ratingInput, { target: { value: '3' } });

    await waitFor(() => {
      expect(componentRegistryService.searchComponents).toHaveBeenCalledWith(
        expect.objectContaining({ minRating: 3 }),
        1,
        10
      );
    });
  });

  it('handles usage filter', async () => {
    render(<FacetedSearchScreen />);

    const usageInput = screen.getByLabelText('Minimum Usage');
    fireEvent.change(usageInput, { target: { value: '50' } });

    await waitFor(() => {
      expect(componentRegistryService.searchComponents).toHaveBeenCalledWith(
        expect.objectContaining({ minUsage: 50 }),
        1,
        10
      );
    });
  });

  it('displays error message when API calls fail', async () => {
    (componentRegistryService.searchComponents as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(<FacetedSearchScreen />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load components. Please try again later.')).toBeInTheDocument();
    });
  });

  it('handles pagination', async () => {
    (componentRegistryService.searchComponents as jest.Mock).mockResolvedValue({
      ...mockSearchResponse,
      total: 25,
    });

    render(<FacetedSearchScreen />);

    await waitFor(() => {
      expect(screen.getByText('Page 1 of 3')).toBeInTheDocument();
    });

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(componentRegistryService.searchComponents).toHaveBeenCalledWith(
        expect.any(Object),
        2,
        10
      );
    });
  });
}); 