import React from 'react';
import { ComponentSummary } from '../../pages/MarketplacePage';

interface ComponentCardProps {
  component: ComponentSummary;
  onSelect: () => void;
}

const ComponentCard: React.FC<ComponentCardProps> = ({ component, onSelect }) => {
  return (
    <div
      onClick={onSelect}
      style={{
        border: '1px solid #ddd',
        borderRadius: 8,
        padding: 16,
        background: '#fff',
        cursor: 'pointer',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        transition: 'box-shadow 0.2s',
      }}
    >
      <h4 style={{ margin: 0 }}>{component.name} <small style={{ color: '#888' }}>(v{component.version})</small></h4>
      <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>{component.type}</div>
      <p style={{ fontSize: 14, minHeight: 40 }}>{component.description.substring(0, 100)}...</p>
      <div style={{ marginBottom: 8 }}>
        {component.tags?.map(tag => (
          <span key={tag} style={{ background: '#e0e7ff', color: '#3730a3', borderRadius: 4, padding: '2px 8px', fontSize: 12, marginRight: 4 }}>{tag}</span>
        ))}
      </div>
      {component.rating !== undefined && (
        <div style={{ fontSize: 12, color: '#f59e42' }}>★ {component.rating.toFixed(1)}</div>
      )}
    </div>
  );
};

export default ComponentCard; 