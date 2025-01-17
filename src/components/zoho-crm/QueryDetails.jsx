// src/components/zoho-crm/QueryDetails.jsx
import React from 'react';

const QueryDetails = ({ queryDetails }) => {
  if (!queryDetails) return null;

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Query Details:</h3>
      <div className="space-y-2">
        <p><strong>Module:</strong> {queryDetails.module}</p>
        <p><strong>Fields:</strong> {queryDetails.fields.join(', ')}</p>
        <p><strong>Criteria:</strong> {queryDetails.criteria || 'None'}</p>
        <p><strong>Page:</strong> {queryDetails.page}</p>
        <p><strong>Records per page:</strong> {queryDetails.per_page}</p>
        <p><strong>Sort by:</strong> {queryDetails.sort_by || 'Default'}</p>
        <p><strong>Sort order:</strong> {queryDetails.sort_order}</p>
      </div>
    </div>
  );
};

export default QueryDetails;