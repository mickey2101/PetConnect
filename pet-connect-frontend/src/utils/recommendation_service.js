/**
 * Enhanced recommendation service that sends local view history
 * to the server-side recommendation engine
 */

import { recommendationsApi } from './apiService';

// Constants
const ANIMAL_VIEWS_KEY = 'pet_connect_animal_views';
const VIEW_TIME_THRESHOLD = 10; // Seconds before a view is considered significant

// Tracking state
let viewStartTime = null;
let currentAnimalId = null;
let viewLogged = false;
let viewUpdateInterval = null;

/**
 * Initialize tracking when viewing an animal
 * 
 * @param {string|number} animalId - The ID of the animal being viewed
 * @param {Object} animalData - Basic animal data to store
 * @returns {Function} - Cleanup function for component unmount
 */
export const initializeTracking = (animalId, animalData = null) => {
  // Set current animal and start time
  currentAnimalId = animalId;
  viewStartTime = new Date();
  viewLogged = false;
  
  // Log initial view
  logAnimalView(animalId, 0, animalData);
  
  // Start tracking view duration
  const stopTracking = startViewDurationTracking(animalId, animalData);
  
  // Return cleanup function
  return () => {
    if (!viewLogged && currentAnimalId) {
      // Log final view duration
      const finalDuration = Math.floor((new Date() - viewStartTime) / 1000);
      logAnimalView(currentAnimalId, finalDuration, animalData);
    }
    
    stopTracking();
    currentAnimalId = null;
  };
};

/**
 * Start tracking view duration
 */
const startViewDurationTracking = (animalId, animalData) => {
  // Clear any existing interval
  if (viewUpdateInterval) {
    clearInterval(viewUpdateInterval);
  }
  
  // Set up interval to update view duration
  viewUpdateInterval = setInterval(() => {
    const viewDuration = Math.floor((new Date() - viewStartTime) / 1000);
    
    // Only log significant views
    if (viewDuration >= VIEW_TIME_THRESHOLD && !viewLogged) {
      logAnimalView(animalId, viewDuration, animalData);
      viewLogged = true;
      
      // Clear interval once logged
      clearInterval(viewUpdateInterval);
      viewUpdateInterval = null;
    }
  }, 5000); // Check every 5 seconds
  
  // Handle page close events
  const handleBeforeUnload = () => {
    if (!viewLogged && animalId) {
      const finalDuration = Math.floor((new Date() - viewStartTime) / 1000);
      logAnimalView(animalId, finalDuration, animalData);
    }
  };
  
  window.addEventListener('beforeunload', handleBeforeUnload);
  
  // Return cleanup function
  return () => {
    clearInterval(viewUpdateInterval);
    window.removeEventListener('beforeunload', handleBeforeUnload);
  };
};

/**
 * Log an animal view to localStorage and server if authenticated
 * 
 * @param {string|number} animalId - ID of the animal being viewed
 * @param {number} viewDuration - Duration of view in seconds
 * @param {Object} animalData - Basic animal data to store
 */
export const logAnimalView = async (animalId, viewDuration, animalData = null) => {
  try {
    // Always store in localStorage
    const viewData = {
      animalId: parseInt(animalId),
      timestamp: new Date().toISOString(),
      viewDuration,
      data: animalData || {}
    };
    
    // Add to local storage
    const views = getLocalViews();
    views.unshift(viewData);
    localStorage.setItem(ANIMAL_VIEWS_KEY, JSON.stringify(views.slice(0, 50)));
    
    // Try to log to server if user is authenticated
    const authToken = getAuthToken();
    if (authToken) {
      await recommendationsApi.logAnimalView({
        animalId,
        viewDuration,
        token: authToken
      });
    }
    
    return true;
  } catch (error) {
    console.error('Error logging animal view:', error);
    return false;
  }
};

/**
 * Get local view history from localStorage
 * @returns {Array} View history objects
 */
export const getLocalViews = () => {
  try {
    const storedViews = localStorage.getItem(ANIMAL_VIEWS_KEY);
    return storedViews ? JSON.parse(storedViews) : [];
  } catch (error) {
    console.error('Error retrieving view history:', error);
    return [];
  }
};

/**
 * Get authentication token from localStorage or session
 * @returns {string|null} Auth token if available
 */
const getAuthToken = () => {
  try {
    // Check where you store the auth token (adjust as needed)
    return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token') || null;
  } catch (error) {
    return null;
  }
};

/**
 * Get personalized recommendations that incorporate local view history
 * 
 * @param {Object} options - Request options
 * @param {number} options.limit - Maximum recommendations to return
 * @param {boolean} options.includeLocalViews - Whether to include local views in request
 * @returns {Promise<Array>} Recommended animals
 */
export const getRecommendations = async (options = {}) => {
  const { limit = 10, includeLocalViews = true } = options;
  
  try {
    // Get auth token
    const token = getAuthToken();
    
    // Prepare request data
    const requestData = {
      limit,
      token
    };
    
    // Include local view history if requested
    if (includeLocalViews) {
      const localViews = getLocalViews();
      if (localViews.length > 0) {
        // Only send necessary data to reduce payload size
        const simplifiedViews = localViews.map(view => ({
          animal_id: view.animalId,
          timestamp: view.timestamp,
          view_duration: view.viewDuration || 0
        }));
        
        requestData.localViewHistory = simplifiedViews;
      }
    }
    
    // Request recommendations from the server
    return await recommendationsApi.getRecommendations(requestData);
  } catch (error) {
    console.error('Error getting recommendations:', error);
    return [];
  }
};

/**
 * Get recently viewed animals
 * 
 * @param {Array} availableAnimals - All available animals to match against
 * @param {number} limit - Maximum animals to return
 * @returns {Array} Recently viewed animals
 */
export const getRecentlyViewedAnimals = (availableAnimals, limit = 5) => {
  const localViews = getLocalViews();
  
  // Extract unique animal IDs
  const uniqueIds = [...new Set(localViews.map(view => view.animalId))];
  const recentIds = uniqueIds.slice(0, limit);
  
  // Map IDs to full animal objects
  return recentIds
    .map(id => availableAnimals.find(a => a.id === id || a.id === parseInt(id)))
    .filter(Boolean);
};

/**
 * Check if user has viewed an animal
 * @param {string|number} animalId - Animal ID to check
 * @returns {boolean} True if viewed
 */
export const hasViewedAnimal = (animalId) => {
  const views = getLocalViews();
  return views.some(view => view.animalId === parseInt(animalId));
};

// Create export object
const recommendationService = {
  initializeTracking,
  logAnimalView,
  getRecommendations,
  getRecentlyViewedAnimals,
  hasViewedAnimal,
  getLocalViews
};

export default recommendationService;