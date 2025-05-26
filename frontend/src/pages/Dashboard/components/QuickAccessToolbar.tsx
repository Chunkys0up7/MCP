import React, { useState } from 'react';
import { Box, Button, TextField, Paper } from '@mui/material';

interface QuickAccessToolbarProps {
  onCreateNew?: () => void; // Optional callback for Create New button
  onSearch?: (searchTerm: string) => void; // Optional callback for search
}

const QuickAccessToolbar: React.FC<QuickAccessToolbarProps> = ({
  onCreateNew,
  onSearch,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleCreateNewClick = () => {
    if (onCreateNew) {
      onCreateNew();
    } else {
      alert('Create New clicked! Placeholder for template selection.');
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (onSearch) {
      onSearch(searchTerm);
    } else {
      console.log(`Search submitted: ${searchTerm}`);
    }
    // Optionally clear search term after submit: setSearchTerm('');
  };

  return (
    <Paper sx={{ p: 2, mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderRadius: 2, boxShadow: 1 }}>
      {/* Create New Button */}
      <Button
        variant="contained"
        color="primary"
        onClick={handleCreateNewClick}
        sx={{ fontWeight: 'bold', borderRadius: 1 }}
      >
        Create New Workflow
      </Button>

      {/* Global Search Form */}
      <Box component="form" onSubmit={handleSearchSubmit} sx={{ display: 'flex', alignItems: 'center' }}>
        <TextField
          type="search"
          placeholder="Global Search..."
          value={searchTerm}
          onChange={handleSearchChange}
          size="small"
          sx={{ mr: 1, minWidth: 220 }}
          inputProps={{ 'aria-label': 'Global Search' }}
        />
        <Button
          type="submit"
          variant="contained"
          color="secondary"
          sx={{ fontWeight: 'bold', borderRadius: 1 }}
        >
          Search
        </Button>
      </Box>
    </Paper>
  );
};

export default QuickAccessToolbar; 