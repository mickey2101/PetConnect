/**
 * Pet Connect - Main App Component
 * -------------------------------
 * The root component of the Pet Connect application that initializes CSRF protection
 * and sets up routes
 * 
 * Author: Macayla van der Merwe
 */

import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { fetchWithCsrf } from './utils/csrfUtils';
import { AuthProvider } from './utils/AuthContext';
import './App.css'; 

// Import your components
import Header from './components/Header';
import HomePage from './pages/HomePage';
import AnimalDetail from './components/AnimalDetail';
import RecommendationsPage from './pages/RecommendationsPage';
import PreferenceForm from './components/PreferenceForm';
import AboutPage from './pages/AboutPage';
import Register from './components/Register';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import ProfilePage from './pages/ProfilePage';
import Animals from './pages/Animals';

function App() {
  // Initialize CSRF token when the app loads
  useEffect(() => {
    const initCsrf = async () => {
      try {
        // Make a request to the CSRF endpoint to set the cookie
        const response = await fetchWithCsrf('/api/csrf/');
        
        if (response.ok) {
          const data = await response.json();
          
          // Store CSRF token in meta tag
          let csrfMeta = document.querySelector('meta[name="csrf-token"]');
          if (!csrfMeta) {
            csrfMeta = document.createElement('meta');
            csrfMeta.setAttribute('name', 'csrf-token');
            document.head.appendChild(csrfMeta);
          }
          csrfMeta.setAttribute('content', data.csrf_token);
          
          // Also store in global variable
          window.csrfToken = data.csrf_token;
          
          console.log('CSRF token initialized successfully');
        } else {
          console.error('Failed to initialize CSRF token: server responded with', response.status);
        }
      } catch (error) {
        console.error('Failed to initialize CSRF token:', error);
      }
    };
    
    initCsrf();
  }, []);
  
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Header />
          <main className="content">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/animals/:animalId" element={<AnimalDetail />} />
              <Route path="/animals" element={<Animals />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/register" element={<Register />} />
              <Route path="/login" element={<Login />} />
              <Route path="/preferences" element={
                <ProtectedRoute>
                  <PreferenceForm />
                </ProtectedRoute>
              } />
             <Route path="/profile" element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              } />
            </Routes>
          </main>
          {/* Footer or other common components */}
        </div>
      </Router>
    </AuthProvider>
  );
  
}

export default App;