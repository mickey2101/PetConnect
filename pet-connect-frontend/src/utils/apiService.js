/**
 * Pet Connect API Service
 * ----------------------
 * Central service for making API calls to the Django backend
 */

import { fetchWithCsrf } from './csrfUtils';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

/**
 * API Methods for Recommendations
 */
export const recommendationsApi = {
  getRecommendations: async ({ animalId = '', limit = 10 } = {}) => {
    try {
      const response = await fetchWithCsrf(
        `${API_BASE_URL}/recommendations/?animal_id=${animalId}&limit=${limit}&_=${Date.now()}`,
        {
          method: 'GET',
          credentials: 'include',
        }
      );

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

  getRecentViews: async ({ limit = 5 } = {}) => {
    try {
      const response = await fetchWithCsrf(
        `${API_BASE_URL}/recommendations/recent-views/?limit=${limit}&_=${Date.now()}`,
        {
          method: 'GET',
          credentials: 'include',
        }
      );

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

  logAnimalView: async ({ animalId, viewDuration = 0 }) => {
    try {
      const formData = new FormData();
      formData.append('animal_id', animalId);
      formData.append('view_duration', viewDuration);

      const response = await fetchWithCsrf(`${API_BASE_URL}/animals/record-view/`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error logging animal view:', error);
      throw error;
    }
  },
};


/**
 * API Methods for Animals
 */
export const animalsApi = {
  /**
   * Get a list of animals with optional filtering
   * 
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Array>} - Array of animal objects
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
      
      const response = await fetchWithCsrf(
        `${API_BASE_URL}/animals/?${queryParams.toString()}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      const data = await response.json();
      return data.animals || [];
    } catch (error) {
      console.error('Error fetching animals:', error);
      return [];
    }
  },
  
  /**
   * Get details for a specific animal
   * 
   * @param {string} animalId - ID of the animal
   * @returns {Promise<Object>} - Animal details object
   */
  getAnimalDetails: async (animalId) => {
    try {
      const response = await fetchWithCsrf(`${API_BASE_URL}/animals/${animalId}/`, {
       method: 'GET',
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
  }
};

/**
 * API Methods for User
 */
export const userApi = {
  /**
   * Get user preferences
   * 
   * @returns {Promise<Object>} - User preferences object
   */
  getUserPreferences: async () => {
    try {
      const response = await fetchWithCsrf(`${API_BASE_URL}/users/preferences/`);
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching user preferences:', error);
      return {};
    }
  },
  
  /**
   * Update user preferences
   * 
   * @param {Object} preferences - New preferences to save
   * @returns {Promise<Object>} - Updated preferences
   */
  updatePreferences: async (preferences) => {
    try {
      const response = await fetchWithCsrf(`${API_BASE_URL}/users/preferences/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(preferences)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error updating user preferences:', error);
      throw error;
    }
  },
  
  /**
   * Log in a user
   * 
   * @param {Object} credentials - User credentials
   * @param {string} credentials.username - Username
   * @param {string} credentials.password - Password
   * @returns {Promise<Object>} - User data
   */
  login: async ({ username, password }) => {
    try {
      const response = await fetchWithCsrf(`${API_BASE_URL}/users/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error logging in:', error);
      throw error;
    }
  },
  
  /**
   * Log out the current user
   * 
   * @returns {Promise<Object>} - Response data
   */
  logout: async () => {
    try {
      const response = await fetchWithCsrf(`${API_BASE_URL}/users/logout/`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error logging out:', error);
      throw error;
    }
  }
};

// Create a named export object
const apiService = {
  recommendations: recommendationsApi,
  animals: animalsApi,
  user: userApi
};

/**
 * Log an animal view with the server using the CORRECT ENDPOINT
 */
export const logAnimalView = async (animalId) => {
  try {
    console.log(`Attempting to log view for animal ${animalId} using animals endpoint...`);
    
    // First, ensure we have a CSRF token
    await fetch(`${API_BASE_URL}/csrf/`, {
      credentials: 'include'
    });
    
    // Use the animals endpoint instead of recommendations
    const response = await fetch(`${API_BASE_URL}/animals/record-view/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'include',
      body: JSON.stringify({ animal_id: animalId })
    });
    
    if (!response.ok) {
      console.error(`View logging failed with status: ${response.status}`);
      try {
        const errorText = await response.text();
        console.error('Error response:', errorText);
      } catch (e) {
        console.error('Could not read error response');
      }
      throw new Error(`HTTP error ${response.status}`);
    }
    
    const data = await response.json();
    console.log('View successfully logged:', data);
    return data;
  } catch (error) {
    console.error('Error logging animal view:', error);
    return null;
  }
};

export default apiService;