import React, { createContext, useState, useEffect, useCallback } from 'react';
import { fetchWithCsrf } from './csrfUtils';
import { API_BASE_URL, isProduction } from './apiConfig';

// Predefined users for production mode - you can modify this
const DEMO_USERS = [
  { 
    id: 1, 
    username: 'demo', 
    password: 'demopassword', 
    email: 'demo@example.com',
    first_name: 'Demo',
    last_name: 'User'
  },
  { 
    id: 2, 
    username: 'Mac',
    password: 'test',
    email: 'admin@example.com',
    first_name: 'Admin',
    last_name: 'User'
  },
  // Add your real test accounts here if needed
];

// Create the AuthContext
export const AuthContext = createContext(null);

// Create the AuthProvider component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [initialized, setInitialized] = useState(false);
  const [authCheckCount, setAuthCheckCount] = useState(0);
  
  // Initialize from localStorage if in production
  useEffect(() => {
    if (isProduction()) {
      const savedUser = localStorage.getItem('petconnect_user');
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          setCurrentUser(userData);
        } catch (e) {
          console.error('Failed to parse saved user data', e);
        }
      }
    }
  }, []);
  
  // Function to check if user is logged in
  const checkAuthStatus = useCallback(async () => {
    // In production, use localStorage authentication
    if (isProduction()) {
      const savedUser = localStorage.getItem('petconnect_user');
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser);
          setCurrentUser(userData);
          setLoading(false);
          setInitialized(true);
          return true;
        } catch (e) {
          console.error('Failed to parse saved user data', e);
        }
      }
      setLoading(false);
      setInitialized(true);
      return false;
    }
    
    // For local environment, use the server check
    if (authCheckCount > 3) {
      console.warn("Auth check attempted too many times, aborting.");
      setLoading(false);
      setInitialized(true);
      return false;
    }
    
    try {
      setLoading(true);
      console.log(`Checking authentication status (attempt ${authCheckCount + 1})...`);
      
      const response = await fetchWithCsrf('/api/users/me/');
      
      if (response.ok) {
        const data = await response.json();
        console.log("Auth check success, user:", data);
        setCurrentUser(data);
        setError(null);
        setAuthCheckCount(0); // Reset counter on success
        setLoading(false);
        setInitialized(true);
        return true;
      } else {
        // If 401/403, user is not authenticated - this is normal
        if (response.status === 401 || response.status === 403) {
          console.log("Auth check: Not authenticated");
          setCurrentUser(null);
          setError(null);
          setAuthCheckCount(0); // Reset counter
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
        }
        setLoading(false);
        setInitialized(true);
        return false;
      }
    } catch (err) {
      console.error('Error checking authentication status:', err);
      setError('Authentication check failed. Please try again later.');
      setCurrentUser(null);
      setAuthCheckCount(prev => prev + 1); // Increment counter
      setLoading(false);
      setInitialized(true);
      return false;
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
      
      // Special handling for production environment
      if (isProduction()) {
        console.log("Using production login flow");
        
        // Simulate a delay for "authentication"
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Check against predefined users
        const matchedUser = DEMO_USERS.find(
          user => user.username.toLowerCase() === username.toLowerCase() && 
                  user.password === password
        );
        
        if (matchedUser) {
          // Create a clean version without password
          const userData = { ...matchedUser };
          delete userData.password;
          
          // Save to state and localStorage
          setCurrentUser(userData);
          localStorage.setItem('petconnect_user', JSON.stringify(userData));
          
          console.log("Production login success:", userData);
          setError(null);
          return userData;
        } else {
          throw new Error('Invalid username or password');
        }
      }
      
      // Local environment: Use normal backend authentication
      console.log("Attempting login with username:", username);
      const response = await fetchWithCsrf('/api/users/login/', {
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
      
      return data;
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please check your credentials and try again.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      setLoading(true);
      
      // For production, just clear localStorage
      if (isProduction()) {
        localStorage.removeItem('petconnect_user');
        setCurrentUser(null);
        setError(null);
        setLoading(false);
        return;
      }
      
      // For local environment, use the API
      const response = await fetchWithCsrf('/api/users/logout/', {
        method: 'POST'
      });
      
      // Clear current user regardless of response
      setCurrentUser(null);
      setError(null);
      
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
      
      // For production, create a simple mock registration
      if (isProduction()) {
        console.log("Using production registration flow");
        
        // Simulate a delay for "processing"
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Check if username already exists
        const userExists = DEMO_USERS.some(
          user => user.username.toLowerCase() === userData.username.toLowerCase()
        );
        
        if (userExists) {
          throw new Error('Username already exists');
        }
        
        // Create a new user with an ID
        const newUser = {
          id: Date.now(),  // Use timestamp as ID
          username: userData.username,
          email: userData.email,
          first_name: userData.first_name || '',
          last_name: userData.last_name || ''
        };
        
        // In a real app, we would add this user to DEMO_USERS,
        // but for a demo we'll just return success without persisting
        
        // Just return success message
        setError(null);
        return { success: true, message: 'Registration successful' };
      }
      
      // For local environment, use the API
      const response = await fetchWithCsrf('/api/users/register/', {
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
      
      // Set error state
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
    isProduction: isProduction()
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