import React, { createContext, useState, useEffect, useCallback } from 'react';
import { fetchWithCsrf } from './csrfUtils';

// Create the AuthContext
export const AuthContext = createContext(null);
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Create the AuthProvider component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [initialized, setInitialized] = useState(false);
  const [authCheckCount, setAuthCheckCount] = useState(0);

  // Function to check if user is logged in
  const checkAuthStatus = useCallback(async () => {
    // Prevent infinite loops - only check 3 times in a row
    if (authCheckCount > 3) {
      console.warn("Auth check attempted too many times, aborting.");
      setLoading(false);
      setInitialized(true);
      return false;
    }
    
    try {
      setLoading(true);
      // Make a request to an endpoint that returns the current user info
      console.log(`Checking authentication status (attempt ${authCheckCount + 1})...`);
      
      const response = await fetchWithCsrf(`${API_BASE_URL}/users/me/`);
      
      if (response.ok) {
        const data = await response.json();
        console.log("Auth check success, user:", data);
        setCurrentUser(data);
        setError(null);
        setAuthCheckCount(0); // Reset counter on success
        return true;
      } else {
        // If 401/403, user is not authenticated - this is normal
        if (response.status === 401 || response.status === 403) {
          console.log("Auth check: Not authenticated");
          setCurrentUser(null);
          setError(null);
          setAuthCheckCount(0); // Reset counter
          return false;
        } else {
          // For other errors, set error state
          try {
            const errorData = await response.json();
            console.error("Auth check error:", errorData);
            setError(errorData.error || 'Authentication check failed');
          } catch (e) {
            console.error("Failed to parse error response:", e);
            setError('Authentication check failed');
          }
          setCurrentUser(null);
          setAuthCheckCount(prev => prev + 1); // Increment counter
          return false;
        }
      }
    } catch (err) {
      console.error('Error checking authentication status:', err);
      setError('Authentication check failed. Please try again later.');
      setCurrentUser(null);
      setAuthCheckCount(prev => prev + 1); // Increment counter
      return false;
    } finally {
      setLoading(false);
      setInitialized(true);
    }
  }, [authCheckCount]);

  // Check auth status when component mounts
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  // Login function
  const login = async (username, password) => {
    try {
      setLoading(true);
      
      // Call login API
      const response = await fetchWithCsrf(`${API_BASE_URL}/users/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });
      
      if (!response.ok) {
        let errorMsg = 'Login failed';
        try {
          const errorData = await response.json();
          errorMsg = errorData.error || errorMsg;
        } catch (e) {
          console.error("Failed to parse error response:", e);
        }
        throw new Error(errorMsg);
      }
      
      const data = await response.json();
      console.log("Login success:", data);
      
      // Set current user
      setCurrentUser(data);
      setError(null);
      setAuthCheckCount(0); // Reset counter on successful login
      
      return data;
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      setLoading(true);
      
      // Call logout API
      const response = await fetchWithCsrf(`${API_BASE_URL}/users/logout/`, {
        method: 'POST'
      });
      
      // Clear current user regardless of response
      setCurrentUser(null);
      setError(null);
      setAuthCheckCount(0); // Reset counter on logout
      
      if (!response.ok) {
        console.warn('Logout API responded with an error, but user was logged out locally');
      }
    } catch (err) {
      console.error('Logout error:', err);
      // Still clear the user even if there's an error
      setCurrentUser(null);
      setError(err.message || 'Logout failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      setLoading(true);
      
      // Make register API call
      const response = await fetchWithCsrf(`${API_BASE_URL}/users/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });
      
      if (!response.ok) {
        let errorMsg = 'Registration failed';
        try {
          const errorData = await response.json();
          errorMsg = errorData.error || errorMsg;
        } catch (e) {
          console.error("Failed to parse error response:", e);
        }
        throw new Error(errorMsg);
      }
      
      const data = await response.json();
      console.log("Registration success:", data);
      
      // Set current user if registration auto-logs in
      if (data) {
        setCurrentUser(data);
        setAuthCheckCount(0); // Reset counter on successful registration
      }
      
      setError(null);
      return data;
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.message || 'Registration failed. Please try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Context value
  const authContextValue = {
    currentUser,
    loading,
    error,
    initialized,
    login,
    logout,
    register,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Create a hook for using the AuthContext
export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};