// src/components/AnimalDetail.js

import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import apiService from '../utils/apiService';
import simpleApi from '../utils/simpleApi';
import { logLocalAnimalView } from '../utils/localStorageViews';
import '../css/animalDetail.css';
import getBreedImageUrl from '../utils/getBreedImageUrl';
import { isProduction } from '../utils/apiConfig';

const AnimalDetail = () => {
  const { animalId } = useParams();
  const navigate = useNavigate();
  const [animal, setAnimal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [viewLogged, setViewLogged] = useState(false);
  // Add new state for shelter popup
  const [showShelterPopup, setShowShelterPopup] = useState(false);
  

  useEffect(() => {
    // Define the data fetching function
    const fetchAnimalData = async () => {
      try {
        setLoading(true);
        
        // Fetch animal details - use different methods for local vs. production
        let animalData;
        if (isProduction()) {
          console.log('Using simple API (no auth) for production');
          animalData = await simpleApi.getAnimalDetails(animalId);
        } else {
          console.log('Using authenticated API call for local');
          animalData = await apiService.animals.getAnimalDetails(animalId);
        }
        
        console.log('Animal details:', animalData);
        setAnimal(animalData);
        
        // Log the view once we have the animal data
        if (!viewLogged && animalId) {
          try {
            // Try server-side logging but don't wait for success
            if (isProduction()) {
              // In production, just log locally
              logLocalAnimalView(animalId, animalData);
              console.log(`Recorded view for animal ${animalId} in localStorage only (production mode)`);
            } else {
              // In local dev, try both server and local
              apiService.recommendations.logAnimalView({ animalId }).catch(error => {
                console.warn('Server-side view logging failed, using local storage only:', error);
              });
              
              // Always log to localStorage as a reliable backup
              logLocalAnimalView(animalId, animalData);
              console.log(`Recorded view for animal ${animalId} in localStorage`);
            }
            
            setViewLogged(true);
          } catch (viewError) {
            console.error('Error logging animal view:', viewError);
            // Continue anyway even if view logging fails
          }
        }
        
        // Fetch recommendations for this animal
        try {
          let recommendationsData;
          if (isProduction()) {
            recommendationsData = await simpleApi.getRecommendations({
              animalId: animalId,
              limit: 3
            });
          } else {
            recommendationsData = await apiService.recommendations.getRecommendations({
              animalId: animalId,
              limit: 3
            });
          }
          
          console.log('Related recommendations:', recommendationsData);
          
          // Filter out any undefined items and the current animal
          const validRecommendations = Array.isArray(recommendationsData) 
            ? recommendationsData.filter(item => item && item.id && item.id !== parseInt(animalId))
            : [];
          
          setRecommendations(validRecommendations);
        } catch (recError) {
          console.error('Error fetching recommendations:', recError);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching animal details:', error);
        setError('Unable to load animal details. Please try again later.');
        setLoading(false);
      }
    };
    
    // Execute the fetch if we have an ID
    if ((animalId)) {
      fetchAnimalData();
    } else {
      setError('No animal ID provided');
      setLoading(false);
    }
  }, [animalId, viewLogged]);

  // Toggle shelter info popup
  const toggleShelterPopup = () => {
    setShowShelterPopup(!showShelterPopup);
  };
  // Add this function to AnimalDetail.js
  const handleEmailShelter = () => {
    // Get shelter email or use a default
    const shelterEmail = animal.shelter?.email || 'contact@shelter.org';
    
    // Create a subject line with the animal's name
    const subject = `Inquiry about adopting ${animal.name}`;
    
    // Create a simple email body
    const body = `Hello,\n\nI'm interested in adopting ${animal.name} (${animal.species}, ${animal.breed || 'Mixed'}).\n\nPlease let me know what the next steps are for the adoption process.\n\nThank you`;
    
    // Encode the subject and body for URL
    const encodedSubject = encodeURIComponent(subject);
    const encodedBody = encodeURIComponent(body);
    
    // Open the mail client
    window.location.href = `mailto:${shelterEmail}?subject=${encodedSubject}&body=${encodedBody}`;
  };

  // Format age display
  const formatAge = (animal) => {
    if (!animal) return '';
    
    const years = animal.age_years || 0;
    const months = animal.age_months || 0;
    
    if (years > 0 && months > 0) {
      return `${years} year${years !== 1 ? 's' : ''}, ${months} month${months !== 1 ? 's' : ''}`;
    } else if (years > 0) {
      return `${years} year${years !== 1 ? 's' : ''}`;
    } else if (months > 0) {
      return `${months} month${months !== 1 ? 's' : ''}`;
    } else {
      return 'Unknown age';
    }
  };

  // Record a view when clicking on a similar animal
  const handleSimilarAnimalClick = async (animalId) => {
    try {
      // Use different approaches for local vs. production
      if (isProduction()) {
        // In production, just log locally
        logLocalAnimalView(animalId);
        console.log(`Recorded view for similar animal ${animalId} in localStorage only (production mode)`);
      } else {
        // In local dev, try both server and local
        apiService.recommendations.logAnimalView({ animalId }).catch(error => {
          console.warn('Server-side view logging failed, using local storage only:', error);
        });
        
        // Always log to localStorage
        logLocalAnimalView(animalId);
        console.log(`Recorded view for similar animal ${animalId} in localStorage`);
      }
    } catch (error) {
      console.error('Error logging animal view:', error);
    }
  };

  // Show loading spinner if still loading
  if (loading) {
    return (
      <div className="container text-center my-5">
        <div className="loading-spinner"></div>
        <p className="loading-text">Loading animal details...</p>
      </div>
    );
  }

  // Show error message if needed
  if (error) {
    return (
      <div className="container my-5">
        <div className="error-alert">{error}</div>
        <button 
          className="primary-button mt-3"
          onClick={() => navigate('/animals')}
        >
          Back to Animal Listings
        </button>
      </div>
    );
  }

  // Early return if no animal data
  if (!animal) {
    return (
      <div className="container my-5">
        <div className="warning-alert">Animal not found.</div>
        <button 
          className="primary-button mt-3"
          onClick={() => navigate('/animals')}
        >
          Back to Animal Listings
        </button>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      {/* Main animal details section */}
      <div className="animal-detail-container">
        <div className="animal-detail-row">
          <div className="animal-image-col">
            <img src={getBreedImageUrl(animal)} alt={animal.name} />
          </div>
          
          <div className="animal-info-col">
            <h1 className="animal-name">{animal.name}</h1>
            
            <div className="animal-badges">
              <span className="badge primary">{animal.species}</span>
              <span className="badge secondary">{animal.breed || 'Mixed'}</span>
              <span className="badge info">{animal.gender}</span>
              <span className="badge light">{formatAge(animal)}</span>
            </div>
            
            <div className="details-card">
              <div className="details-card-header">Animal Details</div>
              <div className="details-card-body">
                <div className="details-row">
                  <div className="details-col">
                    <dl>
                      <dt>Size</dt>
                      <dd>{animal.size || 'Not specified'}</dd>
                      
                      <dt>Energy Level</dt>
                      <dd>{animal.energy_level || 'Not specified'}</dd>
                    </dl>
                  </div>
                  <div className="details-col">
                    <dl>
                      <dt>Good with children</dt>
                      <dd>{animal.good_with_kids ? 'Yes' : 'No'}</dd>
                      
                      <dt>Good with other pets</dt>
                      <dd>
                        {animal.good_with_cats && animal.good_with_dogs ? 'Yes, both cats and dogs' : 
                         animal.good_with_cats ? 'Yes, cats' : 
                         animal.good_with_dogs ? 'Yes, dogs' : 'No'}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="animal-description">
              <h3>About {animal.name}</h3>
              <p>{animal.description || 'No description available.'}</p>
            </div>
            
            {animal.health_info && (
              <div className="animal-health-info">
                <h3>Health Information</h3>
                <p>{animal.health_info}</p>
              </div>
            )}
            
            {animal.behavior_notes && (
              <div className="animal-behavior-notes">
                <h3>Behavior Notes</h3>
                <p>{animal.behavior_notes}</p>
              </div>
            )}
            
            <div className="action-buttons">
              <button className="adopt-button" onClick={toggleShelterPopup}>
                Interested in Adopting {animal.name}
              </button>
              <button 
                className="back-button"
                onClick={() => navigate('/animals')}
              >
                Back to Animal Listings
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Visual separator */}
      <div className="content-separator"></div>
      
      {/* Shelter Popup */}
      {showShelterPopup && (
        <div className="shelter-popup-overlay" onClick={toggleShelterPopup}>
          <div className="shelter-popup-content" onClick={e => e.stopPropagation()}>
            <h2>Contact Shelter</h2>
            <button className="close-popup" onClick={toggleShelterPopup}>×</button>
            
            <div className="shelter-info">
              <h3>{animal.shelter ? animal.shelter.name : 'Animal Shelter'}</h3>
              
              <div className="shelter-contact">
                <p><strong>Address:</strong> {animal.shelter?.address || '123 Shelter Lane, Petsville'}</p>
                <p><strong>Phone:</strong> {animal.shelter?.phone || '(555) 123-4567'}</p>
                <p><strong>Email:</strong> {animal.shelter?.email || 'contact@shelter.org'}</p>
              </div>
              
              <div className="adoption-steps">
                <h4>Next Steps for Adoption:</h4>
                <ol>
                  <li>Contact the shelter via phone or email</li>
                  <li>Schedule a visit to meet {animal.name}</li>
                  <li>Complete adoption application</li>
                  <li>Pay adoption fees</li>
                  <li>Take your new pet home!</li>
                </ol>
              </div>
              
              {/* Update the email button in the shelter popup */}
              <div className="shelter-popup-buttons">
                <button className="email-button" onClick={handleEmailShelter}>
                  Email Shelter
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Similar Animals Section - In a completely separate container */}
      {recommendations.length > 0 && (
        <div className="recommendation-container">
          <h2 className="section-title">You Might Also Like</h2>
          <div className="similar-animals-grid">
            {recommendations.map(rec => (
              rec && rec.id ? (
                <div className="similar-animal-card" key={rec.id}>
                  <div className="similar-animal-image">
                    <img 
                      src={getBreedImageUrl(rec)} 
                      alt={rec.name}
                    />
                  </div>
                  <div className="similar-animal-body">
                    <h3 className="similar-animal-title">{rec.name}</h3>
                    <p className="similar-animal-subtitle">
                      {rec.species} • {rec.breed || 'Mixed'} • {formatAge(rec)}
                    </p>
                    
                    {rec.recommendation_reason && (
                      <div className="info-alert">
                        {rec.recommendation_reason}
                      </div>
                    )}
                    
                    <Link 
                      to={`/animals/${rec.id}`} 
                      className="view-similar-button"
                      onClick={() => handleSimilarAnimalClick(rec.id)}
                    >
                      View {rec.name}
                    </Link>
                  </div>
                </div>
              ) : null
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnimalDetail;