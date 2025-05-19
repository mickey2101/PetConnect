// Updated csrfUtils.js
import { isLocal, getRelativeApiPath } from './apiConfig';

/**
 * CSRF Token Utilities
 * -------------------
 * Handles getting and applying CSRF tokens for API requests
 * 
 * Author: Macayla van der Merwe
 */

/**
 * Get the CSRF token from the page
 * 
 * @returns {string|null} The CSRF token or null if not found
 */
export const getCsrfToken = () => {
  // Look for the token in a meta tag
  const csrfMeta = document.querySelector('meta[name="csrf-token"]');
  if (csrfMeta) {
    return csrfMeta.getAttribute('content');
  }
  
  // Try to get from a cookie
  return getCsrfTokenFromCookie();
};

/**
 * Extract CSRF token from cookies
 * 
 * @returns {string|null} The CSRF token or null if not found
 */
export const getCsrfTokenFromCookie = () => {
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Check for Django's default csrftoken cookie
      if (cookie.substring(0, 10) === 'csrftoken=') {
        return decodeURIComponent(cookie.substring(10));
      }
    }
  }
  return null;
};

/**
 * Fetch a new CSRF token from the server
 * 
 * @returns {Promise<string>} The fetched CSRF token
 */
export const fetchCsrfToken = async () => {
  try {
    // Use env-aware path
    const csrfUrl = getRelativeApiPath('csrf/');
    
    const response = await fetch(csrfUrl, {
      method: 'GET',
      credentials: 'include' // Important for cookies
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch CSRF token: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Successfully fetched CSRF token');
    return data.csrfToken;
  } catch (error) {
    console.error('Error fetching CSRF token:', error);
    return null;
  }
};

/**
 * Apply CSRF token to a fetch options object
 * 
 * @param {Object} options - Fetch options object
 * @returns {Object} Updated options with CSRF headers
 */
export const applyCsrfToken = (options = {}) => {
  const token = getCsrfToken();
  
  if (!token) {
    console.warn('CSRF token not found. API requests may fail.');
    return options;
  }
  
  // Initialize headers if they don't exist
  const headers = options.headers || {};
  
  // Add CSRF token to headers
  return {
    ...options,
    credentials: 'include', // Include cookies with request
    headers: {
      ...headers,
      'X-CSRFToken': token,
      'X-Requested-With': 'XMLHttpRequest'
    }
  };
};

/**
 * Enhanced fetchWithCsrf that will try to get a token if one isn't available
 * The path parameter can be a relative path like 'users/login/' or '/api/users/login/'
 */
export const fetchWithCsrf = async (path, options = {}) => {
  let token = getCsrfToken();
  
  // If no token found, try fetching one
  if (!token) {
    console.log('No CSRF token found, fetching a new one');
    token = await fetchCsrfToken();
    
    // If still no token, proceed without it (will likely fail)
    if (!token) {
      console.warn('Could not fetch CSRF token, proceeding without it');
    }
  }
  
  // Create options with the token
  const optionsWithCsrf = {
    ...options,
    credentials: 'include',
    headers: {
      ...(options.headers || {}),
      'X-CSRFToken': token || '',
      'X-Requested-With': 'XMLHttpRequest'
    }
  };
  
  // Process the URL based on the environment and format
  let url = path;
  
  // If path starts with /api/, keep format but adapt to environment
  if (path.startsWith('/api/')) {
    const endpointPath = path.substring(5); // Remove /api/
    url = getRelativeApiPath(endpointPath);
  } 
  // If it doesn't start with / or http, assume it's a relative API path
  else if (!path.startsWith('/') && !path.startsWith('http')) {
    url = getRelativeApiPath(path);
  }
  // Otherwise keep as is (absolute URL or non-API relative path)
  
  // Log request for debugging
  console.log('Making fetch request with CSRF token:', {
    originalPath: path,
    processedUrl: url,
    method: optionsWithCsrf.method || 'GET',
  });
  
  return fetch(url, optionsWithCsrf);
};

/**
 * Initialize CSRF protection by fetching a token
 * Call this function when your app initializes
 */
export const initializeCsrf = async () => {
  try {
    const token = await fetchCsrfToken();
    console.log('CSRF protection initialized', token ? 'successfully' : 'failed');
    return !!token;
  } catch (error) {
    console.error('Error initializing CSRF protection:', error);
    return false;
  }
};

// Create a named object before exporting
const csrfUtilsService = {
  getCsrfToken,
  getCsrfTokenFromCookie,
  fetchCsrfToken,
  applyCsrfToken,
  fetchWithCsrf,
  initializeCsrf
};

export default csrfUtilsService;