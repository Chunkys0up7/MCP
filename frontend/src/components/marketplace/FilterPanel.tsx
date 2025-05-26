import React from 'react';

interface FilterPanelProps {
  filters: {
    type: string;
    compliance: string[];
    cost: string;
  };
  onFilterChange: (filters: Partial<FilterPanelProps['filters']>) => void;
  searchTerm: string;
  onSearchChange: (term: string) => void;
}

const types = ['LLM', 'Notebook', 'Data'];
const complianceOptions = ['SOC2', 'GDPR', 'HIPAA'];
const costTiers = ['Free', 'Standard', 'Premium'];

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFilterChange, searchTerm, onSearchChange }) => {
  return (
    <div style={{ width: 240, padding: 16, borderRight: '1px solid #eee', background: '#fafbfc' }}>
      <h3>Filters</h3>
      <div style={{ marginBottom: 16 }}>
        <label>Type:</label>
        <select
          value={filters.type}
          onChange={e => onFilterChange({ type: e.target.value })}
          style={{ width: '100%', marginTop: 4 }}
        >
          <option value="">All</option>
          {types.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: 16 }}>
        <label>Compliance:</label>
        <div style={{ marginTop: 4 }}>
          {complianceOptions.map(option => (
            <div key={option}>
              <input
                type="checkbox"
                checked={filters.compliance.includes(option)}
                onChange={e => {
                  const newCompliance = e.target.checked
                    ? [...filters.compliance, option]
                    : filters.compliance.filter(c => c !== option);
                  onFilterChange({ compliance: newCompliance });
                }}
              />
              <span style={{ marginLeft: 8 }}>{option}</span>
            </div>
          ))}
        </div>
      </div>
      <div style={{ marginBottom: 16 }}>
        <label>Cost:</label>
        <select
          value={filters.cost}
          onChange={e => onFilterChange({ cost: e.target.value })}
          style={{ width: '100%', marginTop: 4 }}
        >
          <option value="">All</option>
          {costTiers.map(tier => (
            <option key={tier} value={tier}>{tier}</option>
          ))}
        </select>
      </div>
      <div style={{ marginBottom: 16 }}>
        <label>Search:</label>
        <input
          type="text"
          value={searchTerm}
          onChange={e => onSearchChange(e.target.value)}
          placeholder="Search components..."
          style={{ width: '100%', marginTop: 4, padding: 4 }}
        />
      </div>
    </div>
  );
};

export default FilterPanel; 