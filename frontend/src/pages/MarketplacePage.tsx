import React, { useState, useEffect } from 'react';
import FilterPanel from '../components/marketplace/FilterPanel';
import ComponentCard from '../components/marketplace/ComponentCard';
import ComponentDetailView from '../components/marketplace/ComponentDetailView';
import { searchComponents, getComponentDetails, ComponentSummary, ComponentDetail } from '../services/api';

const MarketplacePage: React.FC = () => {
  const [filters, setFilters] = useState({ type: '', compliance: [], cost: '' });
  const [searchTerm, setSearchTerm] = useState('');
  const [components, setComponents] = useState<ComponentSummary[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<ComponentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch components when filters/search change
  useEffect(() => {
    setIsLoading(true);
    setError(null);
    searchComponents({
      type: filters.type,
      compliance: filters.compliance,
      cost: filters.cost,
      query: searchTerm,
    })
      .then(setComponents)
      .catch((e) => setError(e.message || 'Failed to load components'))
      .finally(() => setIsLoading(false));
  }, [filters, searchTerm]);

  const handleFilterChange = (newFilters: any) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handleComponentSelect = (component: ComponentSummary) => {
    setIsLoading(true);
    setError(null);
    getComponentDetails(component.id)
      .then(setSelectedComponent)
      .catch((e) => setError(e.message || 'Failed to load component details'))
      .finally(() => setIsLoading(false));
  };

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      <FilterPanel
        filters={filters}
        onFilterChange={handleFilterChange}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
      />
      <div style={{ flexGrow: 1, padding: '24px' }}>
        <h2>Component Marketplace</h2>
        {error && <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>}
        {isLoading ? (
          <p>Loading components...</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '20px' }}>
            {components.map((comp) => (
              <ComponentCard key={comp.id} component={comp} onSelect={() => handleComponentSelect(comp)} />
            ))}
          </div>
        )}
      </div>
      {selectedComponent && (
        <ComponentDetailView
          component={selectedComponent}
          onClose={() => setSelectedComponent(null)}
          // Prepare for dependency visualizer integration
          // Pass mock dependency data or a fetch function as needed in the next step
        />
      )}
    </div>
  );
};

export default MarketplacePage; 