/**
 * Pet Connect Recommendation Tracking Module
 * ------------------------------------------
 * This module handles tracking of animal views and updates recommendations
 * dynamically as users browse the website.
 * 
 * Author: Macayla van der Merwe
 */

import { recommendationsApi } from './apiService';

// Configuration
const VIEW_TIME_THRESHOLD = 10; // Seconds before a view is considered significant
const RECOMMENDATION_UPDATE_INTERVAL = 30; // Seconds between recommendation updates

// Track view durations
let viewStartTime = new Date();
let lastRecommendationUpdate = new Date();
let currentAnimalId = null;
let viewLogged = false;
let viewUpdateInterval = null;

/**
 * Initialize tracking when the component mounts
 * 
 * @param {string} animalId - The ID of the animal being viewed
 * @returns {Function} - Cleanup function to call when component unmounts
 */
export const initializeTracking = (animalId) => {
  // Set the current animal ID
  currentAnimalId = animalId;
  
  // Reset tracking variables
  viewStartTime = new Date.now();
  viewLogged = false;
  
  // Log initial view without duration (will be updated later)
  logAnimalView(animalId, 0);
  
  // Start monitoring view duration
  startViewDurationMonitoring(animalId);
  
  // Start periodic recommendation updates
  const stopUpdates = startRecommendationUpdates();
  
  // Clean up when the component unmounts
  return () => {
    if (!viewLogged && currentAnimalId) {
      // Log final view duration
      const finalDuration = Math.floor((new Date.now() - viewStartTime) / 1000);
      logAnimalView(currentAnimalId, finalDuration);
    }
    
    // Clear intervals
    if (viewUpdateInterval) {
      clearInterval(viewUpdateInterval);
    }
    
    // Stop recommendation updates
    stopUpdates();
    
    // Reset variables
    currentAnimalId = null;
  };
};

/**
 * Start monitoring view duration
 * 
 * @param {string} animalId - The ID of the animal being viewed
 */
const startViewDurationMonitoring = (animalId) => {
  // Clear any existing interval
  if (viewUpdateInterval) {
    clearInterval(viewUpdateInterval);
  }
  
  // Set up interval to periodically update view duration
  viewUpdateInterval = setInterval(() => {
    const viewDuration = Math.floor((new Date() - viewStartTime) / 1000);
    
    // Only log significant views (longer than threshold)
    if (viewDuration >= VIEW_TIME_THRESHOLD && !viewLogged) {
      logAnimalView(animalId, viewDuration);
      viewLogged = true;
      
      // Clear the interval once logged
      clearInterval(viewUpdateInterval);
      viewUpdateInterval = null;
    }
  }, 5000); // Check every 5 seconds
  
  // Also set up beforeunload event
  const handleBeforeUnload = () => {
    if (!viewLogged && animalId) {
      const finalDuration = Math.floor((new Date() - viewStartTime) / 1000);
      logAnimalView(animalId, finalDuration);
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
 * Start periodic recommendation updates
 * 
 * @returns {Function} - Function to stop updates
 */
const startRecommendationUpdates = () => {
  // Set up interval to update recommendations
  const updateInterval = setInterval(() => {
    const timeSinceLastUpdate = Math.floor((new Date() - lastRecommendationUpdate) / 1000);
    
    // Only update after the interval has passed
    if (timeSinceLastUpdate >= RECOMMENDATION_UPDATE_INTERVAL) {
      updateRecommendations();
      lastRecommendationUpdate = new Date();
    }
  }, 10000); // Check every 10 seconds
  
  // Return function to stop updates
  return () => clearInterval(updateInterval);
};

/**
 * Log an animal view with the server
 * 
 * @param {string} animalId - The ID of the animal being viewed
 * @param {number} viewDuration - Duration of the view in seconds
 * @returns {Promise<Object>} - Response from the server
 */
export const logAnimalView = async (animalId, viewDuration) => {
  try {
    // Use the API service to log the view
    return await recommendationsApi.logAnimalView({
      animalId,
      viewDuration
    });
  } catch (error) {
    console.error('Error logging animal view:', error);
    return null;
  }
};

/**
 * Update recommendations based on recent views
 * 
 * @returns {Promise<Array>} - Updated recommendations
 */
export const updateRecommendations = async () => {
  try {
    // Get current animal ID, if on an animal page
    const currentId = currentAnimalId || '';
    
    // Get updated recommendations using the API service
    return await recommendationsApi.getRecommendations({
      animalId: currentId
    });
  } catch (error) {
    console.error('Error updating recommendations:', error);
    return [];
  }
};

// Create a named export object
const recommendationTracking = {
  initializeTracking,
  logAnimalView,
  updateRecommendations
};

export default recommendationTracking;