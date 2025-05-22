import React from 'react';
import QuickAccessToolbar from './components/QuickAccessToolbar';

interface PersonalizedFeedScreenProps {
  mlRecommendations?: string[];
  trendingComponents?: string[];
  teamCollaborations?: string[];
}

const PersonalizedFeedScreen: React.FC<PersonalizedFeedScreenProps> = ({
  mlRecommendations = ['Recommendation 1', 'Recommendation 2'], // Default mock data
  trendingComponents = ['Trending Component A', 'Trending Component B'], // Default mock data
  teamCollaborations = ['Team Project X', 'Team Document Y'], // Default mock data
}) => {
  const handleCreateNew = () => {
    // Placeholder for actual create new logic (e.g., navigate to template selection)
    alert('Create New from PersonalizedFeedScreen!');
  };

  const handleSearch = (searchTerm: string) => {
    // Placeholder for actual search logic (e.g., API call, navigate to search results)
    console.log(`PersonalizedFeedScreen received search term: ${searchTerm}`);
  };

  return (
    <div className="p-4">
      <QuickAccessToolbar onCreateNew={handleCreateNew} onSearch={handleSearch} />

      <h1 className="text-2xl font-bold mb-4 pt-4">Dashboard Content Sections</h1>

      {/* ML Recommendations Section */}
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">ML Recommendations</h2>
        {mlRecommendations.length > 0 ? (
          <ul className="list-disc pl-5">
            {mlRecommendations.map((rec, index) => (
              <li key={`rec-${index}`} className="mb-1">{rec}</li>
            ))}
          </ul>
        ) : (
          <p>No recommendations at this time.</p>
        )}
      </section>

      {/* Trending Components Section */}
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Trending Components</h2>
        {trendingComponents.length > 0 ? (
          <ul className="list-disc pl-5">
            {trendingComponents.map((comp, index) => (
              <li key={`comp-${index}`} className="mb-1">{comp}</li>
            ))}
          </ul>
        ) : (
          <p>No trending components available.</p>
        )}
      </section>

      {/* Team Collaborations Section */}
      <section>
        <h2 className="text-xl font-semibold mb-2">Team Collaborations</h2>
        {teamCollaborations.length > 0 ? (
          <ul className="list-disc pl-5">
            {teamCollaborations.map((collab, index) => (
              <li key={`collab-${index}`} className="mb-1">{collab}</li>
            ))}
          </ul>
        ) : (
          <p>No team collaborations to show.</p>
        )}
      </section>
    </div>
  );
};

export default PersonalizedFeedScreen; 