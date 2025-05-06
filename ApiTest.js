import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ApiTest = () => {
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const testApi = async () => {
      try {
        setIsLoading(true);
        const res = await axios.get('/api/test');
        setResponse(res.data);
        setError(null);
      } catch (err) {
        console.error('API test error:', err);
        setResponse(null);
        setError(err.message || 'An error occurred while connecting to the API');
      } finally {
        setIsLoading(false);
      }
    };

    testApi();
  }, []);

  return (
    <div className="api-test" style={{ padding: '20px', marginTop: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
      <h2>API Connection Test</h2>
      {isLoading ? (
        <p>Testing API connection...</p>
      ) : error ? (
        <div style={{ color: 'red' }}>
          <p>Error connecting to API:</p>
          <pre>{error}</pre>
        </div>
      ) : (
        <div style={{ color: 'green' }}>
          <p>Successfully connected to API!</p>
          <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '5px' }}>
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default ApiTest;