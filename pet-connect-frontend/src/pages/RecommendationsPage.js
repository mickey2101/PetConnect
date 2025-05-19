// src/pages/RecommendationsPage.js

import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import apiService from '../utils/apiService';
import getBreedImageUrl from '../utils/getBreedImageUrl';
import { 
  logLocalAnimalView, 
  getLocalAnimalViews, 
  getRecentlyViewedAnimalIds,
  clearLocalAnimalViews
} from '../utils/localStorageViews';
import '../css/recommendation_systels.css';

const RecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [browsedRecommendations, setBrowsedRecommendations] = useState([]);
  const [recentViews, setRecentViews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  // Use useRef instead of useState to prevent re-renders on preference updates
  const lastPreferencesRef = useRef(null);

  // Debug render
  console.log("RecommendationsPage rendering, browsedRecs:", browsedRecommendations);

  // Fetch recommendations and recent views
  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching recommendations and recent views...');
        setLoading(true);
        
        // Get local view data for enhancing recommendations
        const localViewData = getLocalAnimalViews();
        console.log('Local view data available:', localViewData.length, 'items');
        
        // Try to fetch the user's preferences for recommendations
        try {
          const prefsResponse = await apiService.user.getUserPreferences();
          console.log('Current user preferences:', prefsResponse);
          
          // Check if preferences have changed
          if (lastPreferencesRef.current) {
            let preferencesChanged = false;
            
            // Compare key preference fields
            const keysToCompare = ['preferred_species', 'preferred_size', 'preferred_age_min', 
                                  'preferred_age_max', 'preferred_energy_level'];
            
            for (const key of keysToCompare) {
              if (prefsResponse[key] !== lastPreferencesRef.current[key]) {
                console.log(`Preference changed: ${key} from ${lastPreferencesRef.current[key]} to ${prefsResponse[key]}`);
                preferencesChanged = true;
                break;
              }
            }
            
            // If preferences changed, clear local views
            if (preferencesChanged) {
              console.log("Preferences changed! Clearing local view history");
              clearLocalAnimalViews();
            }
          }
          
          // Update last preferences ref (doesn't trigger re-renders)
          lastPreferencesRef.current = prefsResponse;
          
        } catch (prefsError) {
          console.error('Error fetching preferences:', prefsError);
        }
        
        // Fetch recommendations from API
        let validRecommendations = [];
        try {
          const recommendationsData = await apiService.recommendations.getRecommendations({});
          console.log('Received recommendations:', recommendationsData);
          
          // Filter out any undefined items
          validRecommendations = Array.isArray(recommendationsData) 
            ? recommendationsData.filter(item => item && item.id)
            : [];
          
          setRecommendations(validRecommendations);
        } catch (recError) {
          console.error('Error fetching recommendations:', recError);
          setRecommendations([]);
        }
        
        // FORCE browsed recommendations using the local storage IDs directly
        console.log("FORCING browsed recommendations from localStorage...");

        try {
          // Get animal IDs from localStorage
          const recentIds = getRecentlyViewedAnimalIds(5);
          console.log("Recent animal IDs from localStorage:", recentIds);
          
          if (recentIds.length > 0) {
            // Fetch each animal by ID directly
            const browsedRecsPromises = recentIds.map(async (animalId) => {
              try {
                // Fetch this specific animal by ID
                const animalDetails = await apiService.animals.getAnimalDetails(animalId);
                console.log(`Fetched animal ${animalId}:`, animalDetails);
                
                // Return as a recommendation
                return {
                  ...animalDetails,
                  recommendation_reason: `Similar to animals you've viewed`,
                  browsed_recommendation: true
                };
              } catch (err) {
                console.error(`Error fetching animal ${animalId}:`, err);
                return null;
              }
            });
            
            // Wait for all promises to resolve
            const browsedRecsResults = await Promise.all(browsedRecsPromises);
            
            // Filter out nulls (failed fetches)
            const validBrowsedRecs = browsedRecsResults.filter(rec => rec !== null);
            
            // Deduplicate by ID
            const uniqueRecs = [];
            const seenIds = new Set();
            
            for (const rec of validBrowsedRecs) {
              if (!seenIds.has(rec.id)) {
                seenIds.add(rec.id);
                uniqueRecs.push(rec);
              }
            }
            
            console.log("Setting", uniqueRecs.length, "browsed recommendations from localStorage IDs");
            setBrowsedRecommendations(uniqueRecs);
          } else {
            console.log("No recent IDs in localStorage");
            setBrowsedRecommendations([]);
          }
        } catch (err) {
          console.error("Error creating browsed recommendations:", err);
          setBrowsedRecommendations([]);
        }
        
        // First try to fetch recent views from the API
        try {
          const recentViewsData = await apiService.recommendations.getRecentViews({});
          console.log('Received recent views from API:', recentViewsData);
          
          // Filter out any undefined items in recent views
          const validRecentViews = Array.isArray(recentViewsData)
            ? recentViewsData.filter(item => item && item.id)
            : [];
          
          if (validRecentViews.length > 0) {
            // Store API views
            const apiViews = validRecentViews;
            
            // Also fetch local views and merge them
            const localRecentIds = getRecentlyViewedAnimalIds(5);
            const localViews = [];
            
            // Get animal details for locally viewed animals not in API views
            for (const animalId of localRecentIds) {
              // Check if this animal is already in the API views
              if (!apiViews.some(view => view.id === animalId)) {
                try {
                  const animalDetails = await apiService.animals.getAnimalDetails(animalId);
                  const viewData = getLocalAnimalViews().find(v => v.animalId === parseInt(animalId));
                  
                  localViews.push({
                    ...animalDetails,
                    viewed_at: viewData ? viewData.timestamp : new Date().toISOString(),
                    source: 'local' // Mark as from local storage
                  });
                } catch (err) {
                  console.error(`Error fetching details for local animal ${animalId}:`, err);
                }
              }
            }
            
            // Mark API views as from API
            const markedApiViews = apiViews.map(view => ({
              ...view,
              source: 'api'
            }));
            
            // Combine and sort by timestamp
            const combinedViews = [...markedApiViews, ...localViews]
              .sort((a, b) => {
                const aTime = new Date(a.viewed_at || new Date());
                const bTime = new Date(b.viewed_at || new Date());
                return bTime - aTime; // Newest first
              })
              .slice(0, 5); // Limit to 5 items total
            
            setRecentViews(combinedViews);
            console.log('Combined recent views from API and localStorage:', combinedViews);
          } else {
            // If API returned empty array, fall back to local storage
            await fetchLocalRecentViews();
          }
        } catch (viewsError) {
          console.error('Error fetching recent views from API:', viewsError);
          // Fallback to local storage views
          await fetchLocalRecentViews();
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to fetch recommendations. Please try again later.');
        setLoading(false);
      }
    };

    // Function to fetch recently viewed animals from localStorage
    const fetchLocalRecentViews = async () => {
      try {
        console.log('Fetching recent views from localStorage...');
        
        // Get recent animal IDs from localStorage
        const recentIds = getRecentlyViewedAnimalIds(5);
        console.log('Recent animal IDs from localStorage:', recentIds);
        
        if (recentIds.length === 0) {
          setRecentViews([]);
          return;
        }
        
        // Fetch full details for each animal
        const localRecentViews = [];
        for (const animalId of recentIds) {
          try {
            // Get animal details from API
            const animalDetails = await apiService.animals.getAnimalDetails(animalId);
            
            // Find view timestamp from localStorage
            const viewData = getLocalAnimalViews().find(v => v.animalId === parseInt(animalId));
            
            // Add to recent views
            localRecentViews.push({
              ...animalDetails,
              viewed_at: viewData ? viewData.timestamp : new Date().toISOString(),
              source: 'local'
            });
          } catch (err) {
            console.error(`Error fetching details for animal ${animalId}:`, err);
          }
        }
        
        console.log('Local recent views:', localRecentViews);
        setRecentViews(localRecentViews);
      } catch (error) {
        console.error('Error fetching local recent views:', error);
        setRecentViews([]);
      }
    };

    fetchData();
  }, [refreshTrigger]); // Removed lastPreferences from dependency array

  // Record a view when user clicks on an animal
  const handleAnimalClick = async (animalId) => {
    try {
      // Try server-side logging but don't wait for it
      apiService.recommendations.logAnimalView({ animalId }).catch(error => {
        console.warn('Server-side view logging failed, using local storage only:', error);
      });
      
      // Always log locally as a fallback
      logLocalAnimalView(animalId);
      console.log(`Recorded view for animal ${animalId} in localStorage`);
      
      // Refresh recommendations and recent views after recording a view
      setTimeout(() => {
        setRefreshTrigger(prev => prev + 1);
      }, 300);
    } catch (error) {
      console.error('Error recording animal view:', error);
    }
  };

  // Force refresh recommendations
  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  // Manual reset views
  const handleResetViews = () => {
    clearLocalAnimalViews();
    setRefreshTrigger(prev => prev + 1);
  };

  // Get appropriate image URL or fallback
  const getImageUrl = (animal) => {
    if (!animal) return '/static/images/animal-placeholder.jpg';
    return animal.photo_url || '/static/images/animal-placeholder.jpg';
  };

  // Format time ago for recently viewed
  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMin = Math.round(diffMs / 60000);
    
    if (diffMin < 1) return 'Just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    
    const diffHours = Math.floor(diffMin / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  // Show loading state
  if (loading) {
    return (
      <div className="recommendations-container loading">
        <div className="loading-spinner"></div>
        <p>Finding perfect pets for you...</p>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="recommendations-container error">
        <p>{error}</p>
        <button className="retry-button" onClick={handleRefresh}>
          Try Again
        </button>
      </div>
    );
  }

  // Show empty state for recommendations
  if (recommendations.length === 0 && browsedRecommendations.length === 0) {
    return (
      <div className="recommendations-container empty">
        <p>No recommendations available. Please update your preferences or browse more animals.</p>
        
        {/* Still show recently viewed if available */}
        {recentViews.length > 0 && (
          <div className="recently-viewed-container mt-4">
            <h3>Recently Viewed</h3>
            <div className="recently-viewed-cards">
              {recentViews.map(animal => (
                animal && animal.id ? (
                  <div className={`recently-viewed-card ${animal.source === 'local' ? 'local-source' : ''}`} key={animal.id}>
                    <Link 
                      to={`/animals/${animal.id}`}
                      onClick={() => handleAnimalClick(animal.id)}
                    >
                      <img src={getImageUrl(animal)} alt={animal.name} />
                      <div className="recently-viewed-info">
                        <span className="pet-name">{animal.name}</span>
                        <span className="view-time">
                          {animal.viewed_at ? formatTimeAgo(animal.viewed_at) : 'Recently'}
                        </span>
                      </div>
                    </Link>
                  </div>
                ) : null
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Group recommendations by reason
  const groupedRecommendations = recommendations.reduce((groups, animal) => {
    if (!animal || !animal.id) return groups;
    
    // Get reason
    let reason = animal.recommendation_reason || 'Recommended for you';
    
    if (!groups[reason]) {
      groups[reason] = [];
    }
    groups[reason].push(animal);
    return groups;
  }, {});

  return (
    <div>
      <div className="recommendations-container">
        <h2>Your Pet Recommendations</h2>
        <p className="recommendations-subtitle">
          Based on your preferences and browsing history.
          <button className="refresh-button" onClick={handleRefresh}>
            Refresh
          </button>
          <button className="reset-button" onClick={handleResetViews} style={{marginLeft: '8px'}}>
            Reset Views
          </button>
        </p>
        
        {/* Unified Recommendations Section */}
        <div className="unified-recommendations">
          <h3 className="section-title">Recommended Pets For You</h3>
          
          {/* Create a unified array of all recommendations */}
          {(() => {
            // Get all ML-recommendation IDs to check for duplicates
            const mlRecommendationIds = new Set();
            Object.entries(groupedRecommendations).forEach(([reason, animals]) => {
              animals.forEach(animal => {
                mlRecommendationIds.add(animal.id);
              });
            });
            
            // Filter history recommendations to exclude any that also appear in ML recommendations
            const uniqueHistoryRecommendations = browsedRecommendations.filter(
              animal => !mlRecommendationIds.has(animal.id)
            );
            
            // Combine all recommendations into a single array
            const allRecommendations = [
              // Add ML-based recommendations with source marker (these take priority)
              ...Object.entries(groupedRecommendations).flatMap(([reason, animals]) => 
                animals.map((animal, index) => ({
                  ...animal,
                  source: 'ml',
                  reason: reason,
                  score: 100 - (index * 5) // Score decreases with position
                }))
              ),
              
              // Add filtered history-based recommendations with source marker
              ...uniqueHistoryRecommendations.map(animal => ({
                ...animal,
                source: 'history',
                score: 80 // Give history items a lower score than top ML recs
              }))
            ];
            
            // Sort by score (highest first)
            const sortedRecommendations = allRecommendations.sort((a, b) => b.score - a.score);
            
            // Return the grid with all sorted recommendations
            return (
              <div className="all-recommendations-cards">
                {sortedRecommendations.length > 0 ? (
                  sortedRecommendations.map((animal, index) => (
                    <div 
                      className={`pet-card ${animal.source === 'history' ? 'history-based' : 
                                            index < 3 ? 'top-recommendation' : 'standard-recommendation'}`} 
                      key={animal.id}
                    >
                      <Link 
                        to={`/animals/${animal.id}`} 
                        className="pet-card-link"
                        onClick={() => handleAnimalClick(animal.id)}
                      >
                        <div className="pet-card-image">
                          <img src={getBreedImageUrl(animal)} alt={animal.name} />
                          {index === 0 && <div className="best-match-tag">Best Match</div>}
                          {animal.source === 'history' && (
                            <div className="history-tag">Based on History</div>
                          )}
                        </div>
                        <div className="pet-card-content">
                          <h3 className="pet-name">{animal.name}</h3>
                          <p className="pet-breed">{animal.breed || 'Mixed'}</p>
                          <p className="pet-details">
                            {animal.species} • {animal.age_years > 0 ? `${animal.age_years}y` : ''} 
                            {animal.age_months > 0 ? ` ${animal.age_months}m` : ''} • {animal.gender}
                          </p>
                          
                          <div className="pet-match">
                            {/* Use index for color determination, not source */}
                            <div className={`match-indicator ${index < 3 ? 'blue' : 'gray'}`}>
                              <div 
                                className="match-bar" 
                                style={{ width: `${animal.score}%` }}
                              ></div>
                            </div>
                            <span className="match-text">
                              {animal.source === 'history' ? 
                                (index < 3 ? 'Strong match based on your history' : 'Similar to animals you\'ve viewed') :
                                (index === 0 ? 'Strong match!' : 
                                index < 3 ? 'Good match' : 'Potential match')}
                            </span>
                          </div>
                          
                          {animal.reason && (
                            <p className="recommendation-reason">{animal.reason}</p>
                          )}
                          
                          {animal.recommendation_reason && !animal.reason && (
                            <p className="recommendation-reason">{animal.recommendation_reason}</p>
                          )}
                        </div>
                      </Link>
                    </div>
                  ))
                ) : (
                  <div className="no-recommendations">
                    <p>Browse more animals to get recommendations based on your preferences and history</p>
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      </div>
      
      {/* Recently Viewed Section - Kept as is */}
      {recentViews.length > 0 && (
        <div className="recently-viewed-container">
          <h3>Recently Viewed</h3>
          <div className="recently-viewed-cards">
            {recentViews.map(animal => (
              animal && animal.id ? (
                <div className={`recently-viewed-card ${animal.source === 'local' ? 'local-source' : ''}`} key={animal.id}>
                  <Link 
                    to={`/animals/${animal.id}`}
                    onClick={() => handleAnimalClick(animal.id)}
                  >
                    <img src={getBreedImageUrl(animal)} alt={animal.name} />
                    <div className="recently-viewed-info">
                      <span className="pet-name">{animal.name}</span>
                      <span className="view-time">
                        {animal.viewed_at ? formatTimeAgo(animal.viewed_at) : 'Recently'}
                      </span>
                    </div>
                  </Link>
                </div>
              ) : null
            ))}
          </div>
        </div>
      )}
    </div>
  );
  }

export default RecommendationsPage;