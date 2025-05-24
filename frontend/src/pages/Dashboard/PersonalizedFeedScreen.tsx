import React, { useEffect, useState } from 'react';
import QuickAccessToolbar from './components/QuickAccessToolbar';
import { dashboardService, MLRecommendation, TrendingComponent, TeamCollaboration } from '../../services/dashboardService';

const PersonalizedFeedScreen: React.FC = () => {
  const [mlRecommendations, setMLRecommendations] = useState<MLRecommendation[]>([]);
  const [trendingComponents, setTrendingComponents] = useState<TrendingComponent[]>([]);
  const [teamCollaborations, setTeamCollaborations] = useState<TeamCollaboration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const [recommendations, trending, collaborations] = await Promise.all([
          dashboardService.getMLRecommendations(),
          dashboardService.getTrendingComponents(),
          dashboardService.getTeamCollaborations()
        ]);
        
        setMLRecommendations(recommendations);
        setTrendingComponents(trending);
        setTeamCollaborations(collaborations);
        setError(null);
      } catch (err) {
        setError('Failed to load dashboard data. Please try again later.');
        console.error('Error fetching dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleCreateNew = () => {
    // Placeholder for actual create new logic (e.g., navigate to template selection)
    alert('Create New from PersonalizedFeedScreen!');
  };

  const handleSearch = (searchTerm: string) => {
    // Placeholder for actual search logic (e.g., API call, navigate to search results)
    console.log(`PersonalizedFeedScreen received search term: ${searchTerm}`);
  };

  if (isLoading) {
    return (
      <div className="p-4 flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <QuickAccessToolbar onCreateNew={handleCreateNew} onSearch={handleSearch} />
        <div className="text-red-500 mt-4">{error}</div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <QuickAccessToolbar onCreateNew={handleCreateNew} onSearch={handleSearch} />

      <h1 className="text-2xl font-bold mb-4 pt-4">Dashboard Content Sections</h1>

      {/* ML Recommendations Section */}
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">ML Recommendations</h2>
        {mlRecommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mlRecommendations.map((rec) => (
              <div key={rec.id} className="p-4 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
                <h3 className="font-medium">{rec.title}</h3>
                <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-xs text-gray-500">Confidence: {rec.confidence}%</span>
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">{rec.type}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No recommendations at this time.</p>
        )}
      </section>

      {/* Trending Components Section */}
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Trending Components</h2>
        {trendingComponents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {trendingComponents.map((comp) => (
              <div key={comp.id} className="p-4 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
                <h3 className="font-medium">{comp.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{comp.description}</p>
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-xs text-gray-500">Usage: {comp.usageCount}</span>
                  <div className="flex items-center">
                    <span className="text-yellow-500">★</span>
                    <span className="text-xs ml-1">{comp.rating.toFixed(1)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No trending components available.</p>
        )}
      </section>

      {/* Team Collaborations Section */}
      <section>
        <h2 className="text-xl font-semibold mb-2">Team Collaborations</h2>
        {teamCollaborations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {teamCollaborations.map((collab) => (
              <div key={collab.id} className="p-4 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
                <h3 className="font-medium">{collab.name}</h3>
                <p className="text-xs text-gray-500 mt-1">Last modified: {new Date(collab.lastModified).toLocaleDateString()}</p>
                <div className="mt-2">
                  <div className="flex flex-wrap gap-1">
                    {collab.collaborators.map((user, index) => (
                      <span key={index} className="text-xs px-2 py-1 bg-gray-100 rounded-full">{user}</span>
                    ))}
                  </div>
                  <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded mt-2 inline-block">{collab.type}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No team collaborations to show.</p>
        )}
      </section>
    </div>
  );
};

export default PersonalizedFeedScreen; 