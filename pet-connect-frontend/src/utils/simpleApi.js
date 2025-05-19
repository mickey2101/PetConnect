// simpleApi.js - For unauthenticated API calls in production
import { API_BASE_URL, isLocal } from './apiConfig';

/**
 * Simple API service for making unauthenticated requests in production
 * Use this for endpoints that don't require authentication (like getting animals list)
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
  }
};

export default simpleApi;