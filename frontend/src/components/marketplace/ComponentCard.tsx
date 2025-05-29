import React from 'react';
import { ComponentSummary } from '../../services/api';
import Card from '../common/Card';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import Tooltip from '@mui/material/Tooltip';

interface ComponentCardProps {
  component: ComponentSummary;
  onSelect: () => void;
}

const ComponentCard: React.FC<ComponentCardProps> = ({ component, onSelect }) => {
  return (
    <Card
      onClick={onSelect}
      sx={{ cursor: 'pointer', transition: 'box-shadow 0.2s' }}
      title={`${component.name} (v${component.version})`}
    >
      <Typography variant="body2" sx={{ minHeight: 40 }}>
        {component.description.substring(0, 100)}...
      </Typography>
      <div style={{ marginBottom: 8 }} aria-label="Component tags" role="group">
        {component.tags?.map((tag: string) => (
          <Tooltip key={tag} title={`Tag: ${tag}`} arrow>
            <Chip
              label={tag}
              size="small"
              sx={{
                background: '#e0e7ff',
                color: '#3730a3',
                borderRadius: 1,
                fontSize: 12,
                marginRight: 0.5,
                marginBottom: 0.5,
                cursor: 'pointer',
                transition: 'background 0.2s',
                '&:hover': { background: '#c7d2fe' },
                '&:focus': { background: '#a5b4fc' },
              }}
              tabIndex={0}
              role="button"
              aria-label={`Tag: ${tag}`}
            />
          </Tooltip>
        ))}
      </div>
      {component.rating !== undefined && (
        <Typography variant="body2" color="warning.main">★ {component.rating.toFixed(1)}</Typography>
      )}
    </Card>
  );
};

export default ComponentCard; 