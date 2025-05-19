// src/components/RecommendationsList.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/axiosConfig';

function RecommendationsList() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    // Fetch recommendations from the API
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('recommendations/');
      console.log('API Response:', response.data); // Debug
      
      // Handle different response formats
      if (Array.isArray(response.data)) {
        setRecommendations(response.data);
      } else if (response.data.results && Array.isArray(response.data.results)) {
        setRecommendations(response.data.results);
      } else {
        console.error('Unexpected API response format:', response.data);
        setError('Received unexpected data format from the server.');
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setError('Failed to load recommendations. Please try again later.');
      setLoading(false);
    }
  };

  
  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    
    try {
      const response = await api.get('recommendations/refresh/');
      console.log('Refresh Response:', response.data); // Debug
      
      // Handle different response formats
      if (Array.isArray(response.data)) {
        setRecommendations(response.data);
      } else if (response.data.results && Array.isArray(response.data.results)) {
        setRecommendations(response.data.results);
      } else {
        console.error('Unexpected API response format:', response.data);
        setError('Received unexpected data format from the server.');
      }
      setRefreshing(false);
    } catch (error) {
      console.error('Error refreshing recommendations:', error);
      setError('Failed to refresh recommendations. Please try again later.');
      setRefreshing(false);
    }
  };

  if (loading) return <div className="text-center mt-8">Loading your personalized recommendations...</div>;
  if (error) return <div className="text-center mt-8 text-red-600">{error}</div>;

  // Add safety check
  if (!Array.isArray(recommendations)) {
    return <div className="text-center mt-8 text-red-600">Error: Unable to process recommendation data.</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Your Recommended Pets</h1>
        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          {refreshing ? 'Refreshing...' : 'Refresh Recommendations'}
        </button>
      </div>
      
      {recommendations.length === 0 ? (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-6">
          <p className="font-bold">No recommendations yet</p>
          <p>We need more information about your preferences to provide personalized recommendations. 
             Please update your <Link to="/preferences" className="underline">pet preferences</Link>.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendations.map((recommendation) => (
            <div key={recommendation.id} className="bg-white rounded-lg shadow-md overflow-hidden border-2 border-blue-200">
              <div className="p-4">
                <div className="flex justify-between items-start">
                  <h2 className="text-xl font-semibold">{recommendation.animal.name}</h2>
                  <div className="bg-blue-100 text-blue-800 text-sm font-semibold px-2.5 py-0.5 rounded">
                    {Math.round(recommendation.score * 100)}% Match
                  </div>
                </div>
                <p className="text-gray-600">{recommendation.animal.species} - {recommendation.animal.breed}</p>
                <p className="mt-2">
                  Age: {recommendation.animal.age_years > 0 ? `${recommendation.animal.age_years} years` : ''} 
                  {recommendation.animal.age_months > 0 ? ` ${recommendation.animal.age_months} months` : ''}
                </p>
                
                <div className="mt-4">
                  <h3 className="font-medium text-gray-700">Why we think you'll match:</h3>
                  <ul className="mt-1 list-disc list-inside text-sm text-gray-600">
                    {recommendation.match_reasons && Array.isArray(recommendation.match_reasons) ? (
                      recommendation.match_reasons.map((reason, index) => (
                        <li key={index}>{reason}</li>
                      ))
                    ) : (
                      <li>This pet matches your preferences</li>
                    )}
                  </ul>
                </div>
                
                <div className="mt-4">
                  <Link 
                    to={`/animals/${recommendation.animal.id}`}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 inline-block"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RecommendationsList;