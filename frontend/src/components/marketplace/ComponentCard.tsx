import React from 'react';
import { ComponentSummary } from '../../services/api';
import Card from '../common/Card';
import Typography from '@mui/material/Typography';

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
      <div style={{ marginBottom: 8 }}>
        {component.tags?.map((tag: string) => (
          <span key={tag} style={{ background: '#e0e7ff', color: '#3730a3', borderRadius: 4, padding: '2px 8px', fontSize: 12, marginRight: 4 }}>{tag}</span>
        ))}
      </div>
      {component.rating !== undefined && (
        <Typography variant="body2" color="warning.main">★ {component.rating.toFixed(1)}</Typography>
      )}
    </Card>
  );
};

export default ComponentCard; 