// src/utils/apiConfig.js

/**
 * API Configuration
 * ----------------
 * Handles switching between local and production backend URLs
 */

// Define environments
const ENV = {
  LOCAL: 'local',
  PRODUCTION: 'production'
};

// Detect current environment
// If hostname is localhost or 127.0.0.1, use local environment
// URL parameter ?env=local or ?env=production can override
const detectEnvironment = () => {
  // Check URL parameters first (allows testing production URLs locally)
  const urlParams = new URLSearchParams(window.location.search);
  const envParam = urlParams.get('env');
  
  if (envParam === 'local') return ENV.LOCAL;
  if (envParam === 'production') return ENV.PRODUCTION;
  
  // Check hostname
  const isLocalhost = 
    window.location.hostname === 'localhost' || 
    window.location.hostname === '127.0.0.1';
    
  return isLocalhost ? ENV.LOCAL : ENV.PRODUCTION;
};

// URLs for each environment
const API_URLS = {
  [ENV.LOCAL]: 'http://localhost:8000/api',
  [ENV.PRODUCTION]: 'https://petconnect-0a08.onrender.com/api'
};

// Current environment
const CURRENT_ENV = detectEnvironment();

// API base URL for current environment
const API_BASE_URL = API_URLS[CURRENT_ENV];

// Log configuration in development
console.log(`PetConnect API: ${CURRENT_ENV.toUpperCase()} environment (${API_BASE_URL})`);

// Export configuration
export { 
  API_BASE_URL,
  CURRENT_ENV,
  ENV
};

// Helper functions
export const isLocal = () => CURRENT_ENV === ENV.LOCAL;
export const isProduction = () => CURRENT_ENV === ENV.PRODUCTION;

// Build a full API URL with endpoint
export const getApiUrl = (endpoint) => {
  // If endpoint starts with /, remove it
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
  return `${API_BASE_URL}/${normalizedEndpoint}`;
};

// Get a relative API path for use with fetchWithCsrf
export const getRelativeApiPath = (endpoint) => {
  // Make sure endpoint doesn't start with a slash
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
  
  // Return appropriate path format 
  if (isLocal()) {
    // Keep original format for local development
    return `/api/${normalizedEndpoint}`;
  } else {
    // Return absolute URL format for production
    return `${API_BASE_URL}/${normalizedEndpoint}`;
  }
};