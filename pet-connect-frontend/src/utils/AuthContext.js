import React, { createContext, useState, useEffect, useCallback } from 'react';
import { fetchWithCsrf } from './csrfUtils';
import { API_BASE_URL, isProduction } from './apiConfig';

// Create the AuthContext
export const AuthContext = createContext(null);

// Create the AuthProvider component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [initialized, setInitialized] = useState(false);
  const [authCheckCount, setAuthCheckCount] = useState(0);
  
  // In production, we'll use localStorage as a fallback to maintain session
  const [localUserData, setLocalUserData] = useState(() => {
    if (isProduction()) {
      const savedUser = localStorage.getItem('petconnect_user');
      if (savedUser) {
        try {
          return JSON.parse(savedUser);
        } catch (e) {
          console.error('Failed to parse saved user data', e);
          return null;
        }
      }
    }
    return null;
  });
  
  // Save user data to localStorage in production
  useEffect(() => {
    if (isProduction() && currentUser) {
      localStorage.setItem('petconnect_user', JSON.stringify(currentUser));
    }
  }, [currentUser]);

  // Function to check if user is logged in
  const checkAuthStatus = useCallback(async () => {
    // Prevent infinite loops - only check 3 times in a row
    if (authCheckCount > 3) {
      console.warn("Auth check attempted too many times, aborting.");
      setLoading(false);
      setInitialized(true);
      
      // In production, use the localStorage backup if available
      if (isProduction() && localUserData) {
        console.log("Using stored user data in production");
        setCurrentUser(localUserData);
      }
      
      return false;
    }
    
    // In production, use localStorage data first and avoid excessive API calls
    if (isProduction() && localUserData && initialized) {
      console.log("Using cached user data in production");
      setCurrentUser(localUserData);
      setLoading(false);
      return true;
    }
    
    try {
      setLoading(true);
      // Make a request to an endpoint that returns the current user info
      console.log(`Checking authentication status (attempt ${authCheckCount + 1})...`);
      
      const response = await fetchWithCsrf('users/me/');
      
      if (response.ok) {
        const data = await response.json();
        console.log("Auth check success, user:", data);
        setCurrentUser(data);
        
        // In production, also update localStorage
        if (isProduction()) {
          setLocalUserData(data);
        }
        
        setError(null);
        setAuthCheckCount(0); // Reset counter on success
        return true;
      } else {
        // If 401/403, user is not authenticated - this is normal
        if (response.status === 401 || response.status === 403) {
          console.log("Auth check: Not authenticated");
          
          // In production, check if we have localStorage data before clearing
          if (isProduction() && localUserData) {
            console.log("Using stored user data despite auth failure");
            setCurrentUser(localUserData);
            setError(null);
            setAuthCheckCount(0);
            return true;
          }
          
          // Otherwise clear user data
          setCurrentUser(null);
          setLocalUserData(null);
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
          
          // In production, keep using localStorage data if available
          if (isProduction() && localUserData) {
            console.log("Using stored user data despite auth error");
            setCurrentUser(localUserData);
            return true;
          }
          
          setCurrentUser(null);
          setAuthCheckCount(prev => prev + 1); // Increment counter
          return false;
        }
      }
    } catch (err) {
      console.error('Error checking authentication status:', err);
      setError('Authentication check failed. Please try again later.');
      
      // In production, keep using localStorage data if available
      if (isProduction() && localUserData) {
        console.log("Using stored user data despite network error");
        setCurrentUser(localUserData);
        setLoading(false);
        return true;
      }
      
      setCurrentUser(null);
      setAuthCheckCount(prev => prev + 1); // Increment counter
      return false;
    } finally {
      setLoading(false);
      setInitialized(true);
    }
  }, [authCheckCount, initialized, localUserData]);

  // Check auth status when component mounts
  useEffect(() => {
    checkAuthStatus();
    
    // In production, set up a less frequent auth check
    let interval;
    if (isProduction()) {
      // Check every 5 minutes in production to reduce auth calls
      interval = setInterval(() => {
        checkAuthStatus();
      }, 300000); // 5 minutes
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [checkAuthStatus]);

  // Login function
  const login = async (username, password) => {
    try {
      setLoading(true);
      
      // Call login API with environment-aware fetching
      console.log("Attempting login with username:", username);
      const response = await fetchWithCsrf('users/login/', {
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
      
      // In production, also update localStorage
      if (isProduction()) {
        setLocalUserData(data);
      }
      
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
      const response = await fetchWithCsrf('users/logout/', {
        method: 'POST'
      });
      
      // Clear current user and localStorage
      setCurrentUser(null);
      
      if (isProduction()) {
        localStorage.removeItem('petconnect_user');
        setLocalUserData(null);
      }
      
      setError(null);
      setAuthCheckCount(0); // Reset counter on logout
      
      if (!response.ok) {
        console.warn('Logout API responded with an error, but user was logged out locally');
      }
    } catch (err) {
      console.error('Logout error:', err);
      // Still clear the user even if there's an error
      setCurrentUser(null);
      
      if (isProduction()) {
        localStorage.removeItem('petconnect_user');
        setLocalUserData(null);
      }
      
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
      const response = await fetchWithCsrf('users/register/', {
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
        
        // In production, also update localStorage
        if (isProduction()) {
          setLocalUserData(data);
        }
        
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
    checkAuthStatus,
    isProduction: isProduction() // Export for components that need to know the environment
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