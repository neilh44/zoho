// src/components/zoho-crm/ZohoCRMInterface.jsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Database } from 'lucide-react';
import QuerySection from './QuerySection';
import QueryDetails from './QueryDetails';
import ResultsTable from './ResultsTable';

const ZohoCRMInterface = () => {
  const [query, setQuery] = useState('');
  const [queryDetails, setQueryDetails] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  // Sample queries for demonstration
  const sampleQueries = [
    'Show me all open leads from Mumbai',
    'Find all deals worth more than 50000 rupees',
    "List all contacts who haven't been contacted in last 30 days"
  ];

  const handleExecuteQuery = async () => {
    setLoading(true);
    try {
      const response = await fetch('/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      setQueryDetails(data.query_details);
      setResults(data.results);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="h-6 w-6 text-indigo-600" />
              <CardTitle className="text-2xl">Zoho CRM Assistant</CardTitle>
            </div>
            <p className="text-gray-600">Ask questions about your CRM data in natural language</p>
          </CardHeader>

          <CardContent className="space-y-6">
            <QuerySection 
              query={query}
              setQuery={setQuery}
              loading={loading}
              onExecute={handleExecuteQuery}
              sampleQueries={sampleQueries}
            />
            
            <QueryDetails queryDetails={queryDetails} />
            
            <ResultsTable results={results} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ZohoCRMInterface;