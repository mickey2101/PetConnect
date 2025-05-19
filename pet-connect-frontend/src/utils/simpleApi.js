// src/utils/simpleApi.js - Expanded for more endpoints
import { API_BASE_URL, isLocal } from './apiConfig';

/**
 * Simple API service for making unauthenticated requests in production
 * Use this for endpoints that don't require authentication or when in production
 */
const simpleApi = {
  /**
   * Get animals list without authentication
   */
  getAnimals: async (filters = {}) => {
    try {
      // Build query string from filters
      const queryParams = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value);
        }
      });
      
      // Make the request
      console.log(`Fetching animals with simplified API call (no auth)`);
      const response = await fetch(`${API_BASE_URL}/animals/?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        // No credentials in production to avoid CORS issues
        credentials: isLocal() ? 'include' : 'omit'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      const data = await response.json();
      
      // Check response format
      if (Array.isArray(data)) {
        return data;
      } else if (data.animals && Array.isArray(data.animals)) {
        return data.animals;
      } else {
        console.warn('Unexpected response format:', data);
        return [];
      }
    } catch (error) {
      console.error('Error fetching animals:', error);
      return [];
    }
  },

  /**
   * Get animal details without authentication
   */
  getAnimalDetails: async (animalId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/animals/${animalId}/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        // No credentials in production to avoid CORS issues
        credentials: isLocal() ? 'include' : 'omit'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error fetching animal details for ID ${animalId}:`, error);
      throw error;
    }
  },
  
  /**
   * Get recent animal views
   */
  getRecentViews: async (limit = 5) => {
    try {
      const response = await fetch(`${API_BASE_URL}/recommendations/recent-views/?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        },
        credentials: isLocal() ? 'include' : 'omit'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      const data = await response.json();
      return data.recent_views || [];
    } catch (error) {
      console.error('Error fetching recent views:', error);
      return [];
    }
  },
  
  /**
   * Get recommendations for a user
   */
  getRecommendations: async (options = {}) => {
    try {
      // Build query string from options
      const queryParams = new URLSearchParams();
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value);
        }
      });
      
      const response = await fetch(`${API_BASE_URL}/recommendations/?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        },
        credentials: isLocal() ? 'include' : 'omit'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      const data = await response.json();
      return data.recommendations || [];
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return [];
    }
  },
  
  /**
   * Log an animal view (this is a write operation but doesn't necessarily need auth)
   */
  logAnimalView: async (animalId) => {
    try {
      // For production, we might skip this server-side logging
      if (!isLocal()) {
        console.log('Skipping server-side view logging in production mode');
        return { success: true };
      }
      
      const response = await fetch(`${API_BASE_URL}/animals/record-view/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Need credentials for this one
        body: JSON.stringify({ animal_id: animalId })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error logging animal view:', error);
      return null;
    }
  }
};

export default simpleApi;