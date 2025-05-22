import React, { useState } from 'react';

// Mock data for components - replace with API data later
const mockComponents = [
  { id: '1', name: 'Sentiment Analyzer', type: 'AI Model', compliance: 'HIPAA', cost: '0.05/call', description: 'Analyzes text sentiment.' },
  { id: '2', name: 'Data Validator', type: 'Utility', compliance: 'GDPR', cost: '0.01/call', description: 'Validates input data schemas.' },
  { id: '3', name: 'Image Classifier', type: 'AI Model', compliance: 'None', cost: '0.10/image', description: 'Classifies images into categories.' },
  { id: '4', name: 'Notification Service', type: 'Connector', compliance: 'SOC2', cost: '10/month', description: 'Sends notifications via email/sms.' },
];

// Mock filter options
const filterOptions = {
  type: ['All', 'AI Model', 'Utility', 'Connector', 'Data Source'],
  compliance: ['All', 'HIPAA', 'GDPR', 'SOC2', 'None'],
  cost: ['All', 'Free', 'Paid', 'Tiered'], // Simplified cost categories
};

interface Component {
  id: string;
  name: string;
  type: string;
  compliance: string;
  cost: string;
  description: string;
}

const MarketplaceScreen: React.FC = () => {
  const [filters, setFilters] = useState({
    type: 'All',
    compliance: 'All',
    cost: 'All',
  });
  const [searchTerm, setSearchTerm] = useState('');

  // Placeholder for filtered components - actual filtering logic will be added later
  const displayedComponents: Component[] = mockComponents.filter(component => {
    return (
      (filters.type === 'All' || component.type === filters.type) &&
      (filters.compliance === 'All' || component.compliance === filters.compliance) &&
      // Basic text search (name and description)
      (searchTerm === '' || 
       component.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
       component.description.toLowerCase().includes(searchTerm.toLowerCase()))
      // Cost filter logic would be more complex and is omitted for now
    );
  });

  const handleFilterChange = (filterName: keyof typeof filters, value: string) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };
  
  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Trigger search/filter operation if needed, though it's live with displayedComponents
    console.log('Search submitted:', searchTerm);
  };


  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Component Marketplace</h1>

      {/* Filters Section */}
      <div className="mb-8 p-4 bg-gray-50 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          {/* Text Search */}
          <form onSubmit={handleSearchSubmit} className="md:col-span-1">
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">Search Components</label>
            <div className="flex">
              <input
                type="search"
                name="search"
                id="search"
                value={searchTerm}
                onChange={handleSearchChange}
                placeholder="Search by name or description..."
                className="focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-l-md px-3 py-2"
              />
              <button 
                type="submit" 
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-3 rounded-r-md text-sm"
              >
                Go
              </button>
            </div>
          </form>

          {/* Type Filter */}
          <div>
            <label htmlFor="type-filter" className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              id="type-filter"
              name="type-filter"
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm"
            >
              {filterOptions.type.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          {/* Compliance Filter */}
          <div>
            <label htmlFor="compliance-filter" className="block text-sm font-medium text-gray-700 mb-1">Compliance</label>
            <select
              id="compliance-filter"
              name="compliance-filter"
              value={filters.compliance}
              onChange={(e) => handleFilterChange('compliance', e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm"
            >
              {filterOptions.compliance.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          {/* Cost Filter */}
          <div>
            <label htmlFor="cost-filter" className="block text-sm font-medium text-gray-700 mb-1">Cost</label>
            <select
              id="cost-filter"
              name="cost-filter"
              value={filters.cost}
              onChange={(e) => handleFilterChange('cost', e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm"
            >
              {filterOptions.cost.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Components List Section */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Available Components ({displayedComponents.length})</h2>
        {displayedComponents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayedComponents.map(component => (
              <div key={component.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <h3 className="text-xl font-semibold text-indigo-700 mb-2">{component.name}</h3>
                <p className="text-sm text-gray-600 mb-1"><span className="font-medium">Type:</span> {component.type}</p>
                <p className="text-sm text-gray-600 mb-1"><span className="font-medium">Compliance:</span> {component.compliance}</p>
                <p className="text-sm text-gray-600 mb-3"><span className="font-medium">Cost:</span> {component.cost}</p>
                <p className="text-gray-700 mb-4 text-sm">{component.description}</p>
                <button className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded transition-colors text-sm">
                  View Details / Add to Workflow
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-gray-500 py-8">No components match your current filters. Try adjusting your search criteria.</p>
        )}
      </div>
    </div>
  );
};

export default MarketplaceScreen; 