import React, { useEffect, useState } from 'react';
import QuickAccessToolbar from './components/QuickAccessToolbar';
import { dashboardService, MLRecommendation, TrendingComponent, TeamCollaboration } from '../../services/dashboardService';
import { Box, Typography, Grid, Button, CircularProgress, Alert, Chip, Stack } from '@mui/material';
import Card from '../../components/common/Card';

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
      <Box sx={{ p: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }} role="status" aria-busy="true">
        <CircularProgress size={48} />
        <Box sx={{ ml: 2 }}>Loading dashboard...</Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <QuickAccessToolbar onCreateNew={handleCreateNew} onSearch={handleSearch} />
        <Alert severity="error" sx={{ mt: 4 }} role="alert">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4 }}>
      <QuickAccessToolbar onCreateNew={handleCreateNew} onSearch={handleSearch} />

      <Typography variant="h4" fontWeight={700} mb={4} pt={2}>
        Dashboard Content Sections
      </Typography>

      {/* ML Recommendations Section */}
      <Box mb={6} role="region" aria-label="ML Recommendations">
        <Typography variant="h5" fontWeight={600} mb={2}>ML Recommendations</Typography>
        {mlRecommendations.length > 0 ? (
          <Grid container spacing={3}>
            {mlRecommendations.map((rec) => (
              <Grid item xs={12} md={6} lg={4} key={rec.id}>
                <Card sx={{ p: 3, borderRadius: 2, boxShadow: 1, height: '100%', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 4 } }} title={rec.title}>
                  <Typography variant="body2" color="text.secondary" mt={1}>{rec.description}</Typography>
                  <Stack direction="row" spacing={1} mt={2} alignItems="center" justifyContent="space-between">
                    <Chip label={`Confidence: ${rec.confidence}%`} size="small" color="info" />
                    <Chip label={rec.type} size="small" color="primary" />
                  </Stack>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography color="text.secondary" role="region" aria-label="No ML Recommendations">No recommendations at this time.</Typography>
        )}
      </Box>

      {/* Trending Components Section */}
      <Box mb={6} role="region" aria-label="Trending Components">
        <Typography variant="h5" fontWeight={600} mb={2}>Trending Components</Typography>
        {trendingComponents.length > 0 ? (
          <Grid container spacing={3}>
            {trendingComponents.map((comp) => (
              <Grid item xs={12} md={6} lg={4} key={comp.id}>
                <Card sx={{ p: 3, borderRadius: 2, boxShadow: 1, height: '100%', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 4 } }} title={comp.name}>
                  <Typography variant="body2" color="text.secondary" mt={1}>{comp.description}</Typography>
                  <Stack direction="row" spacing={1} mt={2} alignItems="center" justifyContent="space-between">
                    <Chip label={`Usage: ${comp.usageCount}`} size="small" color="default" />
                    <Stack direction="row" spacing={0.5} alignItems="center">
                      <Typography color="warning.main" fontSize={18}>★</Typography>
                      <Typography variant="body2" ml={0.5}>{comp.rating.toFixed(1)}</Typography>
                    </Stack>
                  </Stack>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography color="text.secondary" role="region" aria-label="No Trending Components">No trending components available.</Typography>
        )}
      </Box>

      {/* Team Collaborations Section */}
      <Box role="region" aria-label="Team Collaborations">
        <Typography variant="h5" fontWeight={600} mb={2}>Team Collaborations</Typography>
        {teamCollaborations.length > 0 ? (
          <Grid container spacing={3}>
            {teamCollaborations.map((collab) => (
              <Grid item xs={12} md={6} lg={4} key={collab.id}>
                <Card sx={{ p: 3, borderRadius: 2, boxShadow: 1, height: '100%', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 4 } }} title={collab.name}>
                  <Typography variant="caption" color="text.secondary" mt={1}>
                    Last modified: {new Date(collab.lastModified).toLocaleDateString()}
                  </Typography>
                  <Stack direction="row" spacing={1} mt={2} flexWrap="wrap">
                    {collab.collaborators.map((user, index) => (
                      <Chip key={index} label={user} size="small" sx={{ mb: 0.5 }} />
                    ))}
                  </Stack>
                  <Chip label={collab.type} size="small" color="success" sx={{ mt: 2 }} />
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography color="text.secondary" role="region" aria-label="No Team Collaborations">No team collaborations to show.</Typography>
        )}
      </Box>
    </Box>
  );
};

export default PersonalizedFeedScreen; 