import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import { fetchWithCsrf } from '../utils/csrfUtils';

const ProfilePage = () => {
  const { currentUser, checkAuthStatus } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [preferences, setPreferences] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Form state for editing profile
  const [profileForm, setProfileForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: ''
  });

  // Fetch user profile data
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        
        if (!currentUser) {
          console.log("No user logged in, redirecting to login");
          navigate('/login');
          return;
        }

        // Fetch user data
        const userResponse = await fetchWithCsrf('/api/users/me/');
        
        if (!userResponse.ok) {
          throw new Error(`Failed to fetch user profile: ${userResponse.status}`);
        }
        
        const userData = await userResponse.json();
        
        // Fetch user preferences
        const preferencesResponse = await fetchWithCsrf('/api/users/preferences/');
        let preferencesData = {};
        
        if (preferencesResponse.ok) {
          preferencesData = await preferencesResponse.json();
        }
        
        // Combine user data and preferences
        setProfile(userData);
        setPreferences(preferencesData);
        
        // Initialize form data
        setProfileForm({
          username: userData.username || '',
          email: userData.email || '',
          first_name: userData.first_name || '',
          last_name: userData.last_name || ''
        });
        
        setError(null);
      } catch (err) {
        console.error('Error fetching profile:', err);
        setError('Failed to load profile. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchProfile();
  }, [currentUser, navigate]);

  // Handle form input changes
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle form submission
// Simplified handleProfileSubmit function for ProfilePage.js

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      setSuccessMessage('');
      
      console.log("Submitting profile update:", profileForm);
      
      // Make the API call without CSRF token
      const response = await fetch('/api/users/update-profile/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileForm),
        credentials: 'include'  // This is important to include session cookies
      });
      
      console.log("Profile update response status:", response.status);
      
      if (response.ok) {
        const updatedProfile = await response.json();
        console.log("Updated profile:", updatedProfile);
        setProfile(updatedProfile);
        setEditMode(false);
        setSuccessMessage('Profile updated successfully!');
        
        // Refresh auth context to update currentUser
        checkAuthStatus();
      } else {
        let errorMessage = 'Failed to update profile';
        try {
          const errorData = await response.json();
          console.error("Error data:", errorData);
          errorMessage = errorData.error || errorMessage;
        } catch (parseError) {
          console.error("Error parsing error response:", parseError);
        }
        setError(errorMessage);
      }
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Toggle edit mode
  const toggleEditMode = () => {
    if (editMode) {
      // Reset form to current profile values if canceling
      setProfileForm({
        username: profile.username || '',
        email: profile.email || '',
        first_name: profile.first_name || '',
        last_name: profile.last_name || ''
      });
    }
    setEditMode(!editMode);
    setSuccessMessage('');
    setError(null);
  };

  if (loading && !profile) {
    return <div className="loading">Loading profile...</div>;
  }

  if (error && !profile) {
    return <div className="error-message">{error}</div>;
  }

  if (!profile) {
    return <div className="not-found">Profile not found</div>;
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        <h1>Your Profile</h1>
        
        {successMessage && (
          <div className="success-message">
            {successMessage}
          </div>
        )}
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        <div className="profile-section">
          <div className="section-header">
            <h2>Account Information</h2>
            <button 
              type="button" 
              className="edit-button"
              onClick={toggleEditMode}
            >
              {editMode ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>
          
          {editMode ? (
            <form onSubmit={handleProfileSubmit} className="profile-form">
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={profileForm.username}
                  onChange={handleProfileChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={profileForm.email}
                  onChange={handleProfileChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="first_name">First Name</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={profileForm.first_name}
                  onChange={handleProfileChange}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="last_name">Last Name</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={profileForm.last_name}
                  onChange={handleProfileChange}
                />
              </div>
              
              <div className="form-actions">
                <button type="submit" className="save-button" disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
                <button 
                  type="button" 
                  className="cancel-button" 
                  onClick={toggleEditMode}
                  disabled={loading}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="profile-info">
              <div className="info-item">
                <span className="label">Username:</span>
                <span className="value">{profile.username}</span>
              </div>
              <div className="info-item">
                <span className="label">Email:</span>
                <span className="value">{profile.email}</span>
              </div>
              {profile.first_name && (
                <div className="info-item">
                  <span className="label">First Name:</span>
                  <span className="value">{profile.first_name}</span>
                </div>
              )}
              {profile.last_name && (
                <div className="info-item">
                  <span className="label">Last Name:</span>
                  <span className="value">{profile.last_name}</span>
                </div>
              )}
            </div>
          )}
        </div>
        
        <div className="profile-section">
          <div className="section-header">
            <h2>Adoption Preferences</h2>
            <button 
              className="edit-preferences-button"
              onClick={() => navigate('/preferences')}
            >
              {preferences ? 'Edit Preferences' : 'Set Preferences'}
            </button>
          </div>
          
          {preferences ? (
            <div className="profile-preferences">
              <div className="preference-item">
                <span className="label">Preferred Animal Type:</span>
                <span className="value">{preferences.preferred_species || 'Any'}</span>
              </div>
              <div className="preference-item">
                <span className="label">Age Range:</span>
                <span className="value">
                  {preferences.preferred_age_min || '0'} - {preferences.preferred_age_max || '20'} years
                </span>
              </div>
              <div className="preference-item">
                <span className="label">Preferred Size:</span>
                <span className="value">{preferences.preferred_size || 'Any'}</span>
              </div>
              <div className="preference-item">
                <span className="label">Energy Level:</span>
                <span className="value">{preferences.preferred_energy_level || 'Any'}</span>
              </div>
              <div className="preference-item">
                <span className="label">Good with children:</span>
                <span className="value">{preferences.good_with_children ? 'Yes' : 'No'}</span>
              </div>
              <div className="preference-item">
                <span className="label">Good with other pets:</span>
                <span className="value">{preferences.good_with_other_pets ? 'Yes' : 'No'}</span>
              </div>
            </div>
          ) : (
            <div className="no-preferences">
              <p>You haven't set any preferences yet.</p>
            </div>
          )}
        </div>
        
        <div className="profile-section">
          <h2>Recent Activity</h2>
          <div className="activity-section">
            <button 
              className="view-history-button"
              onClick={() => navigate('/recommendations')}
            >
              View Browsing History
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;