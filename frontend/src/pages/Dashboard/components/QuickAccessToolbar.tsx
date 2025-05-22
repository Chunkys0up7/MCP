import React, { useState } from 'react';

interface QuickAccessToolbarProps {
  onCreateNew?: () => void; // Optional callback for Create New button
  onSearch?: (searchTerm: string) => void; // Optional callback for search
}

const QuickAccessToolbar: React.FC<QuickAccessToolbarProps> = ({
  onCreateNew,
  onSearch,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleCreateNewClick = () => {
    if (onCreateNew) {
      onCreateNew();
    } else {
      alert('Create New clicked! Placeholder for template selection.');
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (onSearch) {
      onSearch(searchTerm);
    } else {
      console.log(`Search submitted: ${searchTerm}`);
    }
    // Optionally clear search term after submit: setSearchTerm('');
  };

  return (
    <div className="p-4 bg-gray-100 rounded-lg shadow mb-6 flex items-center justify-between">
      {/* Create New Button */}
      <button
        onClick={handleCreateNewClick}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Create New Workflow
      </button>

      {/* Global Search Form */}
      <form onSubmit={handleSearchSubmit} className="flex items-center">
        <input
          type="search"
          placeholder="Global Search..."
          value={searchTerm}
          onChange={handleSearchChange}
          className="px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
        <button
          type="submit"
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-r-md"
        >
          Search
        </button>
      </form>
    </div>
  );
};

export default QuickAccessToolbar; 