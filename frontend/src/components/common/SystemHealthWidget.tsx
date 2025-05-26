import React from 'react';
import Card from './Card';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import CircularProgress from '@mui/material/CircularProgress';

export type SystemStatus = 'operational' | 'degraded' | 'partial_outage' | 'major_outage' | 'loading';

interface SystemHealthWidgetProps {
  status: SystemStatus;
  details?: string;
}

const statusConfig = {
  operational: {
    icon: <CheckCircleIcon sx={{ color: 'success.main', fontSize: 32 }} aria-label="Operational" />,
    label: 'All systems operational',
    color: 'success.main',
  },
  degraded: {
    icon: <WarningIcon sx={{ color: 'warning.main', fontSize: 32 }} aria-label="Degraded performance" />,
    label: 'Degraded performance',
    color: 'warning.main',
  },
  partial_outage: {
    icon: <WarningIcon sx={{ color: 'warning.dark', fontSize: 32 }} aria-label="Partial outage" />,
    label: 'Partial outage',
    color: 'warning.dark',
  },
  major_outage: {
    icon: <ErrorIcon sx={{ color: 'error.main', fontSize: 32 }} aria-label="Major outage" />,
    label: 'Major outage',
    color: 'error.main',
  },
  loading: {
    icon: <CircularProgress size={32} aria-label="Loading system status" />,
    label: 'Checking system status...',
    color: 'info.main',
  },
};

const SystemHealthWidget: React.FC<SystemHealthWidgetProps> = ({ status, details }) => {
  const config = statusConfig[status] || statusConfig.operational;
  return (
    <Box role="status" aria-label="System Health Status">
      <Card sx={{ display: 'flex', alignItems: 'center', p: 2, minWidth: 280, bgcolor: 'background.paper' }}>
        <Box sx={{ mr: 2 }}>{config.icon}</Box>
        <Box>
          <Typography variant="subtitle1" fontWeight={600} color={config.color}>{config.label}</Typography>
          {details && <Typography variant="body2" color="text.secondary">{details}</Typography>}
        </Box>
      </Card>
    </Box>
  );
};

export default SystemHealthWidget; 