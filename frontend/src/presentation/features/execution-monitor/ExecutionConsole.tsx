import React, { useState } from 'react';
import { Box, Typography, Button, Checkbox, FormControlLabel } from '@mui/material';
import { useChainStore } from '../../../infrastructure/state/chainStore';

interface ErrorSuggestion {
  id: string;
  text: string;
  checked: boolean;
}

interface ExecutionError {
  message: string;
  suggestions: ErrorSuggestion[];
}

const ExecutionConsole: React.FC = () => {
  const [error, setError] = useState<ExecutionError | null>(null);
  const { executeChain } = useChainStore();

  const handleRetry = async () => {
    try {
      await executeChain();
      setError(null);
    } catch (err) {
      // Example error handling - replace with actual error handling logic
      setError({
        message: 'Invalid input data: Missing required field \'name\' in the input data.',
        suggestions: [
          {
            id: '1',
            text: 'Ensure all required fields are present in the input data.',
            checked: false
          },
          {
            id: '2',
            text: 'Verify the data types of the input fields match the expected types.',
            checked: false
          }
        ]
      });
    }
  };

  const handleSuggestionChange = (suggestionId: string) => {
    if (!error) return;
    
    setError({
      ...error,
      suggestions: error.suggestions.map(suggestion => 
        suggestion.id === suggestionId 
          ? { ...suggestion, checked: !suggestion.checked }
          : suggestion
      )
    });
  };

  if (!error) {
    return (
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 2 }}>
        <Typography variant="h1" sx={{ pb: 3, pt: 5 }}>
          Chain Execution
        </Typography>
        <Button
          variant="contained"
          onClick={handleRetry}
          sx={{ alignSelf: 'flex-end', mt: 'auto' }}
        >
          Execute Chain
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 2 }}>
      <Typography variant="h1" sx={{ pb: 3, pt: 5 }}>
        Execution Failed
      </Typography>
      
      <Typography variant="body1" sx={{ pb: 3, pt: 1 }}>
        The chain execution encountered an error. Please review the error message and suggested fixes below.
      </Typography>

      <Typography variant="h3" sx={{ pb: 2, pt: 4 }}>
        Error Message
      </Typography>
      
      <Typography variant="body1" sx={{ pb: 3, pt: 1 }}>
        {error.message}
      </Typography>

      <Typography variant="h3" sx={{ pb: 2, pt: 4 }}>
        Suggested Fixes
      </Typography>

      <Box sx={{ px: 0 }}>
        {error.suggestions.map((suggestion) => (
          <FormControlLabel
            key={suggestion.id}
            control={
              <Checkbox
                checked={suggestion.checked}
                onChange={() => handleSuggestionChange(suggestion.id)}
                sx={{
                  '&.Mui-checked': {
                    color: 'primary.main',
                  },
                }}
              />
            }
            label={
              <Typography variant="body1">
                {suggestion.text}
              </Typography>
            }
            sx={{ py: 3 }}
          />
        ))}
      </Box>

      <Box sx={{ mt: 'auto', pt: 3, pb: 5 }}>
        <Button
          variant="contained"
          onClick={handleRetry}
          sx={{ float: 'right' }}
        >
          Retry Execution
        </Button>
      </Box>
    </Box>
  );
};

export default ExecutionConsole; 