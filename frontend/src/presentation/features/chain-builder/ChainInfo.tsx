import React from 'react';
import { Box, TextField, Typography } from '@mui/material';
import { useChainStore } from '../../../infrastructure/state/chainStore';

const ChainInfo: React.FC = () => {
  const { chainInfo, updateNode } = useChainStore();

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (chainInfo) {
      updateNode(chainInfo.id, { data: { ...chainInfo, name: event.target.value } });
    }
  };

  const handleDescriptionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (chainInfo) {
      updateNode(chainInfo.id, { data: { ...chainInfo, description: event.target.value } });
    }
  };

  return (
    <Box
      sx={{
        p: 2,
        borderBottom: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
      role="region"
      aria-label="Chain Information"
    >
      <Typography variant="h6" gutterBottom>
        Chain Information
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          label="Chain Name"
          value={chainInfo?.name || ''}
          onChange={handleNameChange}
          required
          fullWidth
          error={!chainInfo?.name}
          helperText={!chainInfo?.name ? 'Chain name is required' : ''}
          inputProps={{
            'aria-label': 'Chain name',
            'aria-required': 'true',
          }}
        />
        <TextField
          label="Description"
          value={chainInfo?.description || ''}
          onChange={handleDescriptionChange}
          fullWidth
          multiline
          rows={2}
          inputProps={{
            'aria-label': 'Chain description',
          }}
        />
      </Box>
    </Box>
  );
};

export default ChainInfo; 