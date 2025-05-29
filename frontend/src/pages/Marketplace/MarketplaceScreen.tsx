import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Button, TextField, Select, MenuItem, InputLabel, FormControl, Alert, CircularProgress, Card, CardContent, CardActions, IconButton } from '@mui/material';
import { PlayArrow as PlayArrowIcon, Info as InfoIcon } from '@mui/icons-material';
import { apiClient } from '../../infrastructure/services/apiClient';
import { useNotification } from '../../infrastructure/context/NotificationContext';

// Define an interface for MCPConfig (mirroring BaseMCPConfig and common fields)
interface MCPConfig {
  id: string;
  name: string;
  type: string;
  description?: string;
}

// Mock filter options - can be dynamic later if needed
const filterOptions = {
  type: ['All', 'llm_prompt', 'jupyter_notebook', 'python_script', 'ai_assistant'],
  compliance: ['All', 'HIPAA', 'GDPR', 'SOC2', 'None'],
  cost: ['All', 'Free', 'Paid', 'Tiered'],
};

const MarketplaceScreen: React.FC = () => {
  const [filters, setFilters] = useState({
    type: 'All',
    compliance: 'All',
    cost: 'All',
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [mcpConfigs, setMcpConfigs] = useState<MCPConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showError, showSuccess } = useNotification();

  // State for individual card run button loading
  const [runningMcpId, setRunningMcpId] = useState<string | null>(null);

  useEffect(() => {
    const fetchMcpConfigs = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await apiClient.get<MCPConfig[]>('/workflows/mcp_configs/');
        setMcpConfigs(response.data);
      } catch (err: any) {
        console.error("Failed to fetch MCP configs:", err);
        setError(err.response?.data?.detail || err.message || 'Failed to load configurations.');
        showError(err.response?.data?.detail || err.message || 'Failed to load configurations.');
      }
      setIsLoading(false);
    };

    fetchMcpConfigs();
  }, [showError]);

  const displayedComponents: MCPConfig[] = mcpConfigs.filter(component => {
    return (
      (filters.type === 'All' || component.type === filters.type) &&
      (searchTerm === '' || 
       component.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
       (component.description && component.description.toLowerCase().includes(searchTerm.toLowerCase())))
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
    console.log('Search submitted:', searchTerm);
  };

  const handleRunMcp = async (mcpId: string) => {
    setRunningMcpId(mcpId);
    try {
      const response = await apiClient.post(`/execute/mcp/${mcpId}`, {});
      showSuccess(`Successfully started execution for MCP: ${mcpId}. Result: ${JSON.stringify(response.data.result)}`);
      console.log("Execution result:", response.data);
    } catch (err: any) {
      console.error(`Failed to run MCP ${mcpId}:`, err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to run MCP.';
      showError(errorMessage);
    }
    setRunningMcpId(null);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Alert severity="info" sx={{ mb: 3 }} role="region" aria-label="Onboarding Tip">
        Welcome to the Marketplace! Browse, filter, and search for components to add to your workflows. All cards and filters are fully responsive and accessible.
      </Alert>
      <Typography variant="h4" fontWeight={700} mb={4} textAlign="center">
        Component Marketplace
      </Typography>

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 6 }} role="status" aria-busy="true">
          <CircularProgress size={40} />
          <Box sx={{ ml: 2 }}>Loading configurations...</Box>
        </Box>
      )}
      {error && !isLoading && (
        <Alert severity="error" sx={{ mb: 2 }} role="alert">{error}</Alert>
      )}

      <Paper sx={{ mb: 6, p: 3, borderRadius: 2, boxShadow: 1 }}>
        <Grid container spacing={3} alignItems="flex-end">
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

      <Box role="region" aria-label="Available Components">
        <Typography variant="h5" fontWeight={600} mb={3}>
          Available MCPs ({displayedComponents.length})
        </Typography>
        {!isLoading && !error && displayedComponents.length > 0 ? (
          <Grid container spacing={4}>
            {displayedComponents.map(mcp => (
              <Grid item xs={12} md={6} lg={4} key={mcp.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', borderRadius: '8px', boxShadow: 3, '&:hover': { boxShadow: 6 } }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', color: 'primary.dark' }}>
                      {mcp.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" mb={0.5}><strong>ID:</strong> {mcp.id}</Typography>
                    <Typography variant="body2" color="text.secondary" mb={0.5}><strong>Type:</strong> {mcp.type}</Typography>
                    <Typography variant="body2" color="text.primary" mb={2}>{mcp.description || 'No description available.'}</Typography>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
                    <Button 
                      variant="contained" 
                      color="primary" 
                      startIcon={runningMcpId === mcp.id ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                      onClick={() => handleRunMcp(mcp.id)} 
                      disabled={runningMcpId === mcp.id || !!runningMcpId}
                    >
                      {runningMcpId === mcp.id ? 'Running...' : 'Run'}
                    </Button>
                    <IconButton aria-label="info" size="small">
                      <InfoIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : !isLoading && !error && (
          <Alert severity="info" sx={{ textAlign: 'center', py: 6 }} role="region" aria-label="No Components">
            No MCP configurations found or match your current filters. Check if MCPs are defined in the 'examples' directory.
          </Alert>
        )}
      </Box>
    </Box>
  );
};

export default MarketplaceScreen; 