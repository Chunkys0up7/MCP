import React, { useState } from 'react';
import { Box, Typography, Paper, Grid, Button, TextField, Select, MenuItem, InputLabel, FormControl, Alert, CircularProgress } from '@mui/material';

// Mock data for components - replace with API data later
const mockComponents = [
  { id: '1', name: 'Sentiment Analyzer', type: 'AI Model', compliance: 'HIPAA', cost: '0.05/call', description: 'Analyzes text sentiment.' },
  { id: '2', name: 'Data Validator', type: 'Utility', compliance: 'GDPR', cost: '0.01/call', description: 'Validates input data schemas.' },
  { id: '3', name: 'Image Classifier', type: 'AI Model', compliance: 'None', cost: '0.10/image', description: 'Classifies images into categories.' },
  { id: '4', name: 'Notification Service', type: 'Connector', compliance: 'SOC2', cost: '10/month', description: 'Sends notifications via email/sms.' },
];

// Mock filter options
const filterOptions = {
  type: ['All', 'AI Model', 'Utility', 'Connector', 'Data Source'],
  compliance: ['All', 'HIPAA', 'GDPR', 'SOC2', 'None'],
  cost: ['All', 'Free', 'Paid', 'Tiered'], // Simplified cost categories
};

interface Component {
  id: string;
  name: string;
  type: string;
  compliance: string;
  cost: string;
  description: string;
}

const MarketplaceScreen: React.FC = () => {
  const [filters, setFilters] = useState({
    type: 'All',
    compliance: 'All',
    cost: 'All',
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false); // Future: set true when loading
  const [error, setError] = useState<string | null>(null); // Future: set error message

  // Placeholder for filtered components - actual filtering logic will be added later
  const displayedComponents: Component[] = mockComponents.filter(component => {
    return (
      (filters.type === 'All' || component.type === filters.type) &&
      (filters.compliance === 'All' || component.compliance === filters.compliance) &&
      // Basic text search (name and description)
      (searchTerm === '' || 
       component.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
       component.description.toLowerCase().includes(searchTerm.toLowerCase()))
      // Cost filter logic would be more complex and is omitted for now
    );
  });

  const handleFilterChange = (filterName: keyof typeof filters, value: string) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };
  
  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Trigger search/filter operation if needed, though it's live with displayedComponents
    console.log('Search submitted:', searchTerm);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Onboarding tip */}
      <Alert severity="info" sx={{ mb: 3 }} role="region" aria-label="Onboarding Tip">
        Welcome to the Marketplace! Browse, filter, and search for components to add to your workflows. All cards and filters are fully responsive and accessible.
      </Alert>
      <Typography variant="h4" fontWeight={700} mb={4} textAlign="center">
        Component Marketplace
      </Typography>

      {/* Global loading and error states */}
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 6 }} role="status" aria-busy="true">
          <CircularProgress size={40} />
          <Box sx={{ ml: 2 }}>Loading components...</Box>
        </Box>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} role="alert">{error}</Alert>
      )}

      {/* Filters Section */}
      <Paper sx={{ mb: 6, p: 3, borderRadius: 2, boxShadow: 1 }}>
        <Grid container spacing={3} alignItems="flex-end">
          {/* Text Search */}
          <Grid item xs={12} md={3}>
            <Box component="form" onSubmit={handleSearchSubmit} sx={{ display: 'flex', alignItems: 'center' }}>
              <TextField
                type="search"
                name="search"
                id="search"
                value={searchTerm}
                onChange={handleSearchChange}
                placeholder="Search by name or description..."
                size="small"
                fullWidth
                sx={{ mr: 1 }}
                label="Search Components"
                inputProps={{ 'aria-label': 'Search Components' }}
              />
              <Button type="submit" variant="contained" color="primary" sx={{ fontWeight: 'bold', borderRadius: 1 }}>
                Go
              </Button>
            </Box>
          </Grid>

          {/* Type Filter */}
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel id="type-filter-label">Type</InputLabel>
              <Select
                labelId="type-filter-label"
                id="type-filter"
                value={filters.type}
                label="Type"
                onChange={(e) => handleFilterChange('type', e.target.value)}
              >
                {filterOptions.type.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>

          {/* Compliance Filter */}
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel id="compliance-filter-label">Compliance</InputLabel>
              <Select
                labelId="compliance-filter-label"
                id="compliance-filter"
                value={filters.compliance}
                label="Compliance"
                onChange={(e) => handleFilterChange('compliance', e.target.value)}
              >
                {filterOptions.compliance.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>

          {/* Cost Filter */}
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel id="cost-filter-label">Cost</InputLabel>
              <Select
                labelId="cost-filter-label"
                id="cost-filter"
                value={filters.cost}
                label="Cost"
                onChange={(e) => handleFilterChange('cost', e.target.value)}
              >
                {filterOptions.cost.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Components List Section */}
      <Box role="region" aria-label="Available Components">
        <Typography variant="h5" fontWeight={600} mb={3}>
          Available Components ({displayedComponents.length})
        </Typography>
        {displayedComponents.length > 0 ? (
          <Grid container spacing={4}>
            {displayedComponents.map(component => (
              <Grid item xs={12} md={6} lg={4} key={component.id}>
                <Paper sx={{ p: 3, borderRadius: 2, boxShadow: 1, height: '100%', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 4 } }}>
                  <Typography variant="h6" color="primary" fontWeight={600} mb={1}>{component.name}</Typography>
                  <Typography variant="body2" color="text.secondary" mb={0.5}><strong>Type:</strong> {component.type}</Typography>
                  <Typography variant="body2" color="text.secondary" mb={0.5}><strong>Compliance:</strong> {component.compliance}</Typography>
                  <Typography variant="body2" color="text.secondary" mb={1}><strong>Cost:</strong> {component.cost}</Typography>
                  <Typography variant="body2" color="text.primary" mb={2}>{component.description}</Typography>
                  <Button variant="contained" color="success" fullWidth sx={{ fontWeight: 500 }}>
                    View Details / Add to Workflow
                  </Button>
                </Paper>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Alert severity="info" sx={{ textAlign: 'center', py: 6 }} role="region" aria-label="No Components">
            No components match your current filters. Try adjusting your search criteria.
          </Alert>
        )}
      </Box>
    </Box>
  );
};

export default MarketplaceScreen; 