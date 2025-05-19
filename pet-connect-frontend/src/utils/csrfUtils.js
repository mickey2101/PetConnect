// Updated csrfUtils.js - Frontend-only fix
import { isLocal, getRelativeApiPath, API_BASE_URL, ENV, CURRENT_ENV } from './apiConfig';

/**
 * CSRF Token Utilities with CORS production fixes (frontend only)
 */

/**
 * Get the CSRF token from the page
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
 */
export const fetchCsrfToken = async () => {
  try {
    // Use env-aware path
    const csrfUrl = getRelativeApiPath('csrf/');
    
    const response = await fetch(csrfUrl, {
      method: 'GET',
      // For production, avoid credentials for this call to prevent CORS issues
      credentials: isLocal() ? 'include' : 'omit'
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
    credentials: isLocal() ? 'include' : 'omit', // Only include credentials in local mode
    headers: {
      ...headers,
      'X-CSRFToken': token,
      'X-Requested-With': 'XMLHttpRequest'
    }
  };
};

/**
 * Enhanced fetchWithCsrf with CORS production workarounds
 */
export const fetchWithCsrf = async (path, options = {}) => {
  // Get token (primarily for local development)
  let token = getCsrfToken();
  
  // If no token found, try fetching one
  if (!token && isLocal()) {
    console.log('No CSRF token found, fetching a new one');
    token = await fetchCsrfToken();
    
    // If still no token, proceed without it (will likely fail)
    if (!token) {
      console.warn('Could not fetch CSRF token, proceeding without it');
    }
  }
  
  // Prepare options with token for local mode
  // For production, avoid sending credentials which cause CORS issues
  const optionsWithCsrf = {
    ...options,
    credentials: isLocal() ? 'include' : 'omit', // Key change for production
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
  
  // Log request for debugging
  console.log('Making fetch request with CSRF token:', {
    originalPath: path,
    processedUrl: url,
    method: optionsWithCsrf.method || 'GET',
    environment: CURRENT_ENV,
    credentials: optionsWithCsrf.credentials
  });
  
  return fetch(url, optionsWithCsrf);
};

/**
 * Initialize CSRF protection by fetching a token
 * Call this function when your app initializes
 */
export const initializeCsrf = async () => {
  // Only fetch CSRF token in local mode
  if (!isLocal()) {
    console.log('Skipping CSRF initialization in production mode to avoid CORS issues');
    return true;
  }
  
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