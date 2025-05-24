import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import PersonalizedFeedScreen from './PersonalizedFeedScreen';
import { dashboardService } from '../../services/dashboardService';

// Mock the dashboard service
jest.mock('../../services/dashboardService', () => ({
  dashboardService: {
    getMLRecommendations: jest.fn(),
    getTrendingComponents: jest.fn(),
    getTeamCollaborations: jest.fn(),
  },
}));

describe('PersonalizedFeedScreen', () => {
  const mockRecommendations = [
    {
      id: '1',
      title: 'Test Recommendation',
      description: 'Test Description',
      confidence: 85,
      type: 'component' as const,
    },
  ];

  const mockTrending = [
    {
      id: '1',
      name: 'Test Component',
      description: 'Test Description',
      usageCount: 100,
      rating: 4.5,
    },
  ];

  const mockCollaborations = [
    {
      id: '1',
      name: 'Test Collaboration',
      lastModified: '2024-03-24T12:00:00Z',
      collaborators: ['User 1', 'User 2'],
      type: 'workflow' as const,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading state initially', () => {
    render(<PersonalizedFeedScreen />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays error message when API calls fail', async () => {
    (dashboardService.getMLRecommendations as jest.Mock).mockRejectedValue(new Error('API Error'));
    (dashboardService.getTrendingComponents as jest.Mock).mockRejectedValue(new Error('API Error'));
    (dashboardService.getTeamCollaborations as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(<PersonalizedFeedScreen />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load dashboard data. Please try again later.')).toBeInTheDocument();
    });
  });

  it('displays data when API calls succeed', async () => {
    (dashboardService.getMLRecommendations as jest.Mock).mockResolvedValue(mockRecommendations);
    (dashboardService.getTrendingComponents as jest.Mock).mockResolvedValue(mockTrending);
    (dashboardService.getTeamCollaborations as jest.Mock).mockResolvedValue(mockCollaborations);

    render(<PersonalizedFeedScreen />);

    await waitFor(() => {
      // Check ML Recommendations
      expect(screen.getByText('Test Recommendation')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
      expect(screen.getByText('Confidence: 85%')).toBeInTheDocument();

      // Check Trending Components
      expect(screen.getByText('Test Component')).toBeInTheDocument();
      expect(screen.getByText('Usage: 100')).toBeInTheDocument();
      expect(screen.getByText('4.5')).toBeInTheDocument();

      // Check Team Collaborations
      expect(screen.getByText('Test Collaboration')).toBeInTheDocument();
      expect(screen.getByText('User 1')).toBeInTheDocument();
      expect(screen.getByText('User 2')).toBeInTheDocument();
    });
  });

  it('displays empty state messages when no data is available', async () => {
    (dashboardService.getMLRecommendations as jest.Mock).mockResolvedValue([]);
    (dashboardService.getTrendingComponents as jest.Mock).mockResolvedValue([]);
    (dashboardService.getTeamCollaborations as jest.Mock).mockResolvedValue([]);

    render(<PersonalizedFeedScreen />);

    await waitFor(() => {
      expect(screen.getByText('No recommendations at this time.')).toBeInTheDocument();
      expect(screen.getByText('No trending components available.')).toBeInTheDocument();
      expect(screen.getByText('No team collaborations to show.')).toBeInTheDocument();
    });
  });
}); 