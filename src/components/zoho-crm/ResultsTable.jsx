// src/components/zoho-crm/ResultsTable.jsx
import React from 'react';
import { Table } from '../ui/table';

const ResultsTable = ({ results }) => {
  if (!results || !results.records || results.records.length === 0) return null;

  return (
    <div>
      <div className="overflow-x-auto">
        <Table>
          <thead>
            <tr className="bg-gray-50">
              {Object.keys(results.records[0]).map((header) => (
                <th key={header} className="px-4 py-2 text-left text-sm font-medium text-gray-700">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.records.map((record, index) => (
              <tr key={index} className="border-t">
                {Object.values(record).map((value, valueIndex) => (
                  <td key={valueIndex} className="px-4 py-2 text-sm text-gray-900">
                    {value || '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
      <div className="mt-4 text-sm text-gray-600">
        Showing {results.records.length} of {results.count} records
        {results.more_records && ' (More records available)'}
      </div>
    </div>
  );
};

export default ResultsTable;