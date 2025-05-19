import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';

/**
 * Protected route component that redirects to login if user is not authenticated
 */
const ProtectedRoute = ({ children }) => {
  const { currentUser, loading, initialized, checkAuthStatus } = useAuth();
  const location = useLocation();
  const [authChecked, setAuthChecked] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [checkCount, setCheckCount] = useState(0);
  
  // Force a single recheck of authentication status when the component mounts
  useEffect(() => {
    const verifyAuth = async () => {
      // Only check once when we mount
      if (!authChecked && checkCount < 2) {
        console.log("Protected route: Checking auth status");
        
        try {
          const isAuth = await checkAuthStatus();
          setIsAuthenticated(isAuth);
        } catch (error) {
          console.error("Error checking auth:", error);
          setIsAuthenticated(false);
        } finally {
          setAuthChecked(true);
          setCheckCount(prev => prev + 1);
        }
      }
    };
    
    verifyAuth();
  }, [authChecked, checkAuthStatus, checkCount]);
  
  // Show loading spinner while checking authentication
  if (loading && !authChecked) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
        
        <style jsx>{`
          .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 40vh;
            width: 100%;
          }
          
          .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top-color: #3498db;
            animation: spin 1s ease-in-out infinite;
            margin-bottom: 16px;
          }
          
          @keyframes spin {
            to {
              transform: rotate(360deg);
            }
          }
        `}</style>
      </div>
    );
  }
  
  // If auth check is complete and user is not authenticated, redirect to login
  if (authChecked && !isAuthenticated && !currentUser) {
    console.log("Protected route: Redirecting to login");
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // We're authenticated now
  if (currentUser || isAuthenticated) {
    console.log("Protected route: User authenticated, rendering children");
    return children;
  }
  
  // Fallback to checking currentUser directly as a last resort
  if (initialized && !loading) {
    if (!currentUser) {
      console.log("Protected route: Not authenticated after init, redirecting to login");
      return <Navigate to="/login" state={{ from: location }} replace />;
    } else {
      console.log("Protected route: User authenticated via currentUser check");
      return children;
    }
  }
  
  // Default loading state
  return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p>Verifying authentication...</p>
      
      <style jsx>{`
        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 40vh;
          width: 100%;
        }
        
        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid rgba(0, 0, 0, 0.1);
          border-radius: 50%;
          border-top-color: #3498db;
          animation: spin 1s ease-in-out infinite;
          margin-bottom: 16px;
        }
        
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

export default ProtectedRoute;