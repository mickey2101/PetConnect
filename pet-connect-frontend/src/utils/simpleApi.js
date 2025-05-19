// Updated simpleApi.js with authentication handling
import { API_BASE_URL, isLocal } from './apiConfig';

/**
 * Simple API service with authentication fallback
 * First tries without auth, then falls back to credentials if needed
 */
const simpleApi = {
  /**
   * Get animals list with authentication fallback
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
      
      // First try without credentials in production
      if (!isLocal()) {
        try {
          console.log(`Trying to fetch animals without auth`);
          const response = await fetch(`${API_BASE_URL}/animals/?${queryParams.toString()}`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            // No credentials to avoid CORS issues
            credentials: 'omit'
          });
          
          // If successful, return the data
          if (response.ok) {
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
          }
          
          // If 403, try again with credentials
          if (response.status === 403) {
            console.log('Server requires authentication. Trying with credentials...');
            // Fall through to the authenticated request
          } else {
            throw new Error(`HTTP error ${response.status}`);
          }
        } catch (noAuthError) {
          console.warn('Failed to fetch without authentication:', noAuthError);
          // Fall through to the authenticated request
        }
      }
      
      // If local or the no-auth request failed, use credentials
      console.log(`Fetching animals with credentials`);
      const response = await fetch(`${API_BASE_URL}/animals/?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        // Include credentials
        credentials: 'include'
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
   * Get animal details with authentication fallback
   */
  getAnimalDetails: async (animalId) => {
    try {
      // First try without credentials in production
      if (!isLocal()) {
        try {
          console.log(`Trying to fetch animal ${animalId} without auth`);
          const response = await fetch(`${API_BASE_URL}/animals/${animalId}/`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            // No credentials to avoid CORS issues
            credentials: 'omit'
          });
          
          // If successful, return the data
          if (response.ok) {
            return await response.json();
          }
          
          // If 403, try again with credentials
          if (response.status === 403) {
            console.log('Server requires authentication. Trying with credentials...');
            // Fall through to the authenticated request
          } else {
            throw new Error(`HTTP error ${response.status}`);
          }
        } catch (noAuthError) {
          console.warn('Failed to fetch without authentication:', noAuthError);
          // Fall through to the authenticated request
        }
      }
      
      // If local or the no-auth request failed, use credentials
      console.log(`Fetching animal ${animalId} with credentials`);
      const response = await fetch(`${API_BASE_URL}/animals/${animalId}/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        // Include credentials
        credentials: 'include'
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
   * Get recent animal views with authentication fallback
   */
  getRecentViews: async (limit = 5) => {
    try {
      // First try without credentials in production
      if (!isLocal()) {
        try {
          console.log(`Trying to fetch recent views without auth`);
          const response = await fetch(`${API_BASE_URL}/recommendations/recent-views/?limit=${limit}`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json'
            },
            credentials: 'omit'
          });
          
          // If successful, return the data
          if (response.ok) {
            const data = await response.json();
            return data.recent_views || [];
          }
          
          // If 403, use localStorage instead
          if (response.status === 403) {
            console.log('Server requires authentication for recent views.');
            return [];
          } else {
            throw new Error(`HTTP error ${response.status}`);
          }
        } catch (noAuthError) {
          console.warn('Failed to fetch recent views:', noAuthError);
          return [];
        }
      }
      
      // If local environment, use credentials
      console.log(`Fetching recent views with credentials`);
      const response = await fetch(`${API_BASE_URL}/recommendations/recent-views/?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        },
        credentials: 'include'
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
   * Get recommendations with authentication fallback
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
      
      // First try without credentials in production
      if (!isLocal()) {
        try {
          console.log(`Trying to fetch recommendations without auth`);
          const response = await fetch(`${API_BASE_URL}/recommendations/?${queryParams.toString()}`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json'
            },
            credentials: 'omit'
          });
          
          // If successful, return the data
          if (response.ok) {
            const data = await response.json();
            return data.recommendations || [];
          }
          
          // If 403, try again with credentials
          if (response.status === 403) {
            console.log('Server requires authentication. Trying with credentials...');
            // Fall through to the authenticated request
          } else {
            throw new Error(`HTTP error ${response.status}`);
          }
        } catch (noAuthError) {
          console.warn('Failed to fetch without authentication:', noAuthError);
          // Fall through to the authenticated request
        }
      }
      
      // If local or the no-auth request failed, use credentials
      console.log(`Fetching recommendations with credentials`);
      const response = await fetch(`${API_BASE_URL}/recommendations/?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        },
        credentials: 'include'
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
   * Log an animal view (this is a write operation and will definitely need auth)
   */
  logAnimalView: async (animalId) => {
    try {
      console.log(`Logging view for animal ${animalId} with auth`);
      const response = await fetch(`${API_BASE_URL}/animals/record-view/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Always need credentials for this one
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