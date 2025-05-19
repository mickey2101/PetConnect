import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchWithCsrf } from '../utils/csrfUtils';
import { useAuth } from '../utils/AuthContext';

const PreferenceForm = () => {
  const { currentUser, checkAuthStatus } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [preferences, setPreferences] = useState({
    preferred_species: '',
    preferred_age_min: 0,
    preferred_age_max: 20,
    preferred_size: '',
    preferred_energy_level: '',
    good_with_children: false,
    good_with_other_pets: false
  });

  useEffect(() => {
    // First, make sure currentUser is available by checking auth status
    const initializeAuth = async () => {
      if (!currentUser) {
        console.log("No current user, checking auth status");
        await checkAuthStatus();
      } else {
        console.log("Current user found:", currentUser);
        fetchPreferences();
      }
    };
    
    initializeAuth();
  }, [currentUser]);

  // Separate function to fetch preferences
  const fetchPreferences = async () => {
    try {
      setLoading(true);
      // Get CSRF token first to ensure the cookie is set
      await fetchWithCsrf('/api/csrf/');
      
      console.log("Fetching preferences...");
      const response = await fetchWithCsrf('/api/users/preferences/', {
        headers: {
          'Accept': 'application/json'
        }
      });
      
      console.log("Preferences response:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("Fetched preferences:", data);
        setPreferences(prev => ({
          ...prev,
          ...data
        }));
        setError(null);
      } else {
        // If 404, that's fine - it means no preferences set yet
        if (response.status !== 404) {
          let errorMsg = 'Failed to load preferences';
          try {
            const errorData = await response.json();
            console.error("Error fetching preferences:", errorData);
            errorMsg = errorData.error || errorMsg;
          } catch (e) {
            console.error("Could not parse error response:", e);
          }
          setError(errorMsg);
          
          // Check for authentication errors
          if (response.status === 403) {
            console.log("Authentication error - refreshing auth status");
            await checkAuthStatus();
          }
        }
      }
    } catch (err) {
      console.error('Error fetching preferences:', err);
      setError('Failed to load preferences. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setPreferences(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      setSuccessMessage('');
      
      // Make sure we have a currentUser before submitting
      if (!currentUser) {
        console.log("No current user - refreshing auth status");
        await checkAuthStatus();
        
        if (!currentUser) {
          setError('You must be logged in to save preferences');
          return;
        }
      }

      console.log("Submitting preferences:", preferences);
      
      // First get a fresh CSRF token
      await fetchWithCsrf('/api/csrf/');
      
      // Use a basic fetch first to debug CSRF issues
      const response = await fetch('/api/users/preferences/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'include',
        body: JSON.stringify(preferences)
      });
      
      console.log("Save response status:", response.status);
      
      if (response.ok) {
        let data;
        try {
          data = await response.json();
        } catch (e) {
          console.log("Response wasn't JSON but succeeded");
          data = { success: true };
        }
        
        console.log("Preferences saved successfully:", data);
        setSuccessMessage('Preferences saved successfully!');
        // Optionally navigate to recommendations page after saving
        // navigate('/recommendations');
      } else {
        let errorMsg = 'Failed to save preferences';
        try {
          const errorData = await response.json();
          console.error("Error saving preferences:", errorData);
          errorMsg = errorData.error || errorMsg;
        } catch (e) {
          console.error("Could not parse error response:", e);
        }
        setError(errorMsg);
        
        // Check for authentication errors
        if (response.status === 403) {
          console.log("Authentication error - refreshing auth status");
          await checkAuthStatus();
          setError('Authentication error. Please try logging in again.');
        }
      }
    } catch (err) {
      console.error('Error saving preferences:', err);
      setError('Failed to save preferences. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !preferences) {
    return <div className="loading">Loading preferences...</div>;
  }

  return (
    <div className="preference-form-container">
      <h2>Your Adoption Preferences</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="preference-form">
        <div className="form-group">
          <label htmlFor="preferred_species">Preferred Animal Type</label>
          <select
            id="preferred_species"
            name="preferred_species"
            value={preferences.preferred_species || ''}
            onChange={handleChange}
          >
            <option value="">Any</option>
            <option value="Dog">Dog</option>
            <option value="Cat">Cat</option>
            <option value="Small Animal">Small Animal</option>
            <option value="Bird">Bird</option>
            <option value="Reptile">Reptile</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>Age Range</label>
          <div className="age-range-inputs">
            <div>
              <label htmlFor="preferred_age_min">Min</label>
              <input
                type="number"
                id="preferred_age_min"
                name="preferred_age_min"
                min="0"
                max="20"
                value={preferences.preferred_age_min || 0}
                onChange={handleChange}
              />
            </div>
            <div>
              <label htmlFor="preferred_age_max">Max</label>
              <input
                type="number"
                id="preferred_age_max"
                name="preferred_age_max"
                min="0"
                max="20"
                value={preferences.preferred_age_max || 20}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="preferred_size">Preferred Size</label>
          <select
            id="preferred_size"
            name="preferred_size"
            value={preferences.preferred_size || ''}
            onChange={handleChange}
          >
            <option value="">Any</option>
            <option value="Small">Small</option>
            <option value="Medium">Medium</option>
            <option value="Large">Large</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="preferred_energy_level">Energy Level</label>
          <select
            id="preferred_energy_level"
            name="preferred_energy_level"
            value={preferences.preferred_energy_level || ''}
            onChange={handleChange}
          >
            <option value="">Any</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>
        
        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              name="good_with_children"
              checked={preferences.good_with_children || false}
              onChange={handleChange}
            />
            Good with children
          </label>
        </div>
        
        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              name="good_with_other_pets"
              checked={preferences.good_with_other_pets || false}
              onChange={handleChange}
            />
            Good with other pets
          </label>
        </div>
        
        <div className="form-actions">
          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PreferenceForm;