import React, { useEffect, useState, useCallback } from 'react';
import { componentRegistryService, Component, ComponentFilter, SearchResponse } from '../../services/componentRegistryService';
import { useDebounce } from '../../hooks/useDebounce';

const FacetedSearchScreen: React.FC = () => {
  const [components, setComponents] = useState<Component[]>([]);
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [minRating, setMinRating] = useState<number>(0);
  const [minUsage, setMinUsage] = useState<number>(0);
  const [availableTypes, setAvailableTypes] = useState<string[]>([]);
  const [popularTags, setPopularTags] = useState<string[]>([]);
  const [facets, setFacets] = useState<SearchResponse['facets']>({ types: {}, tags: {} });

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  const fetchComponents = useCallback(async () => {
    try {
      setIsLoading(true);
      const filters: ComponentFilter = {
        searchTerm: debouncedSearchTerm,
        type: selectedTypes.length > 0 ? selectedTypes : undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
        minRating: minRating > 0 ? minRating : undefined,
        minUsage: minUsage > 0 ? minUsage : undefined,
      };

      const response = await componentRegistryService.searchComponents(
        filters,
        currentPage,
        pageSize
      );

      setComponents(response.components);
      setTotalResults(response.total);
      setFacets(response.facets);
      setError(null);
    } catch (err) {
      setError('Failed to load components. Please try again later.');
      console.error('Error fetching components:', err);
    } finally {
      setIsLoading(false);
    }
  }, [debouncedSearchTerm, selectedTypes, selectedTags, minRating, minUsage, currentPage, pageSize]);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [types, tags] = await Promise.all([
          componentRegistryService.getAvailableTypes(),
          componentRegistryService.getPopularTags(),
        ]);
        setAvailableTypes(types);
        setPopularTags(tags);
      } catch (err) {
        console.error('Error fetching initial data:', err);
      }
    };

    fetchInitialData();
  }, []);

  useEffect(() => {
    fetchComponents();
  }, [fetchComponents]);

  const handleTypeToggle = (type: string) => {
    setSelectedTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const handleTagToggle = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  if (isLoading && components.length === 0) {
    return (
      <div className="p-4 flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex gap-4">
        {/* Facets Sidebar */}
        <div className="w-64 flex-shrink-0">
          <div className="sticky top-4">
            <h2 className="text-lg font-semibold mb-4">Filters</h2>
            
            {/* Search Input */}
            <div className="mb-4">
              <input
                type="text"
                placeholder="Search components..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-2 border rounded"
              />
            </div>

            {/* Type Filter */}
            <div className="mb-4">
              <h3 className="font-medium mb-2">Types</h3>
              <div className="space-y-2">
                {availableTypes.map(type => (
                  <label key={type} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedTypes.includes(type)}
                      onChange={() => handleTypeToggle(type)}
                      className="mr-2"
                    />
                    <span>{type} ({facets.types[type] || 0})</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Tags Filter */}
            <div className="mb-4">
              <h3 className="font-medium mb-2">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {popularTags.map(tag => (
                  <button
                    key={tag}
                    onClick={() => handleTagToggle(tag)}
                    className={`px-2 py-1 rounded text-sm ${
                      selectedTags.includes(tag)
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                  >
                    {tag} ({facets.tags[tag] || 0})
                  </button>
                ))}
              </div>
            </div>

            {/* Rating Filter */}
            <div className="mb-4">
              <h3 className="font-medium mb-2">Minimum Rating</h3>
              <input
                type="range"
                min="0"
                max="5"
                step="0.5"
                value={minRating}
                onChange={(e) => setMinRating(parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="text-sm text-gray-600">{minRating} stars</div>
            </div>

            {/* Usage Filter */}
            <div className="mb-4">
              <h3 className="font-medium mb-2">Minimum Usage</h3>
              <input
                type="number"
                min="0"
                value={minUsage}
                onChange={(e) => setMinUsage(parseInt(e.target.value) || 0)}
                className="w-full p-2 border rounded"
              />
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="flex-grow">
          {error ? (
            <div className="text-red-500">{error}</div>
          ) : (
            <>
              <div className="mb-4">
                <h1 className="text-2xl font-bold">Components</h1>
                <p className="text-gray-600">{totalResults} results found</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {components.map(component => (
                  <div
                    key={component.id}
                    className="p-4 border rounded-lg shadow-sm hover:shadow-md transition-shadow"
                  >
                    <h3 className="font-medium">{component.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{component.description}</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {component.tags.map(tag => (
                        <span
                          key={tag}
                          className="text-xs px-2 py-1 bg-gray-100 rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <div className="mt-2 flex justify-between items-center">
                      <div className="flex items-center">
                        <span className="text-yellow-500">★</span>
                        <span className="text-sm ml-1">{component.rating.toFixed(1)}</span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {component.usageCount} uses
                      </span>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      <p>Version: {component.version}</p>
                      <p>Last updated: {new Date(component.lastUpdated).toLocaleDateString()}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalResults > pageSize && (
                <div className="mt-4 flex justify-center gap-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-3 py-1 border rounded disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <span className="px-3 py-1">
                    Page {currentPage} of {Math.ceil(totalResults / pageSize)}
                  </span>
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage >= Math.ceil(totalResults / pageSize)}
                    className="px-3 py-1 border rounded disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FacetedSearchScreen; 