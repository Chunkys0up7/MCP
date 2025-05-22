import React from 'react';
import { render, screen } from '@testing-library/react';
import PersonalizedFeedScreen from './PersonalizedFeedScreen';

describe('PersonalizedFeedScreen', () => {
  it('renders all section titles', () => {
    render(<PersonalizedFeedScreen />);

    // Check for the main title
    expect(screen.getByText('Personalized Dashboard')).toBeInTheDocument();

    // Check for section titles
    expect(screen.getByText('ML Recommendations')).toBeInTheDocument();
    expect(screen.getByText('Trending Components')).toBeInTheDocument();
    expect(screen.getByText('Team Collaborations')).toBeInTheDocument();
  });

  it('renders placeholder text when data is empty', () => {
    render(
      <PersonalizedFeedScreen
        mlRecommendations={[]}
        trendingComponents={[]}
        teamCollaborations={[]}
      />
    );

    expect(screen.getByText('No recommendations at this time.')).toBeInTheDocument();
    expect(screen.getByText('No trending components available.')).toBeInTheDocument();
    expect(screen.getByText('No team collaborations to show.')).toBeInTheDocument();
  });

  it('renders list items when data is available', () => {
    const mockData = {
      mlRecommendations: ['ML Rec 1', 'ML Rec 2'],
      trendingComponents: ['Trend Comp A', 'Trend Comp B'],
      teamCollaborations: ['Collab Project Z'],
    };
    render(<PersonalizedFeedScreen {...mockData} />);

    expect(screen.getByText('ML Rec 1')).toBeInTheDocument();
    expect(screen.getByText('Trend Comp A')).toBeInTheDocument();
    expect(screen.getByText('Collab Project Z')).toBeInTheDocument();
  });
}); 