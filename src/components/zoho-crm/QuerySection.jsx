// src/components/zoho-crm/QuerySection.jsx
import React from 'react';
import { Search, ArrowRight } from 'lucide-react';

const QuerySection = ({ query, setQuery, loading, onExecute, sampleQueries }) => {
  return (
    <div className="space-y-6">
      {/* Query Input */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
          <Search className="h-4 w-4" />
          Your Query
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full px-4 py-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 min-h-[100px]"
          placeholder="Enter your query here..."
        />
        
        <div className="flex justify-between items-center pt-2">
          <button
            onClick={onExecute}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            disabled={loading}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
            ) : (
              <ArrowRight className="h-4 w-4" />
            )}
            Execute Query
          </button>
        </div>
      </div>

      {/* Sample Queries */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Sample Queries:</h3>
        <div className="space-y-2">
          {sampleQueries.map((sampleQuery, index) => (
            <button
              key={index}
              onClick={() => setQuery(sampleQuery)}
              className="block w-full text-left px-3 py-2 rounded hover:bg-gray-100 text-indigo-600 hover:text-indigo-800 text-sm transition-colors"
            >
              <ArrowRight className="h-4 w-4 inline mr-2" />
              {sampleQuery}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QuerySection;