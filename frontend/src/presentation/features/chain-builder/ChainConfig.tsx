import React from 'react';
import {
  Box,
  Typography,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton,
  Paper,
  Alert,
  CircularProgress,
  Button,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import SaveIcon from '@mui/icons-material/Save';
import { useChainStore } from '../../../infrastructure/state/chainStore';
import { useNotification } from '../../../infrastructure/context/NotificationContext';
import { useKeyboardShortcuts } from '../../../infrastructure/hooks/useKeyboardShortcuts';
import ConfirmationDialog from '../../components/ConfirmationDialog';
import { useChainOperations } from '../../../infrastructure/hooks/useChainOperations';
import type { ChainConfig } from '../../../infrastructure/types/chain';

interface Props {
  nodeId: string;
  config: ChainConfig;
}

const ChainConfigComponent: React.FC<Props> = ({ nodeId, config }) => {
  const { handleUpdateNode } = useChainOperations();

  const handleErrorHandlingChange = (field: keyof ChainConfig['errorHandling'], value: number | boolean) => {
    if (!config) return;

    const newConfig = {
      ...config,
      errorHandling: {
        ...config.errorHandling,
        [field]: value,
      },
    };

    handleUpdateNode(nodeId, { config: newConfig });
  };

  const handleGeneralConfigChange = (field: 'timeout' | 'maxConcurrent', value: number) => {
    if (!config) return;

    const newConfig = {
      ...config,
      [field]: value,
    };

    handleUpdateNode(nodeId, { config: newConfig });
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Chain Configuration
      </Typography>
      <Box sx={{ mt: 2 }}>
        <TextField
          label="Retry Count"
          type="number"
          value={config?.errorHandling?.retryCount || 0}
          onChange={(e) => handleErrorHandlingChange('retryCount', parseInt(e.target.value) || 0)}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Retry Delay (ms)"
          type="number"
          value={config?.errorHandling?.retryDelay || 1000}
          onChange={(e) => handleErrorHandlingChange('retryDelay', parseInt(e.target.value) || 1000)}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Timeout (ms)"
          type="number"
          value={config?.timeout || 30000}
          onChange={(e) => handleGeneralConfigChange('timeout', parseInt(e.target.value) || 30000)}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Max Concurrent"
          type="number"
          value={config?.maxConcurrent || 1}
          onChange={(e) => handleGeneralConfigChange('maxConcurrent', parseInt(e.target.value) || 1)}
          fullWidth
          margin="normal"
        />
      </Box>
    </Box>
  );
};

export default ChainConfigComponent; 