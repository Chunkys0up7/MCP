import React, { useState } from 'react';
import { Box, Button, TextField, Paper } from '@mui/material';
import Tooltip from '@mui/material/Tooltip';

interface QuickAccessToolbarProps {
  onCreateNew?: () => void; // Optional callback for Create New button
  onSearch?: (searchTerm: string) => void; // Optional callback for search
}

const buttonSx = {
  fontWeight: 'bold',
  borderRadius: 1,
  minWidth: 44,
  minHeight: 44,
  transition: 'background 0.2s, box-shadow 0.2s',
  '&:hover': { background: '#f3f6fa', boxShadow: 3 },
  '&:focus': { background: '#e3eefd', boxShadow: '0 0 0 3px #1976d2' },
};

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
      <Tooltip title="Create a new workflow" arrow>
        <Button
          variant="contained"
          color="primary"
          onClick={handleCreateNewClick}
          sx={buttonSx}
          aria-label="Create New Workflow"
        >
          Create New Workflow
        </Button>
      </Tooltip>

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
        <Tooltip title="Search the dashboard" arrow>
          <Button
            type="submit"
            variant="contained"
            color="secondary"
            sx={buttonSx}
            aria-label="Search"
          >
            Search
          </Button>
        </Tooltip>
      </Box>
    </Paper>
  );
};

export default QuickAccessToolbar; 