import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import getBreedImageUrl from '../utils/getBreedImageUrl';

const Animals = () => {
  const [animals, setAnimals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    species: '',
    gender: '',
    age_min: '',
    age_max: '',
    size: '',
    energy_level: ''
  });

  useEffect(() => {
    const fetchAnimals = async () => {
      try {
        setLoading(true);

        // Construct query params from filters
        const queryParams = new URLSearchParams();

        Object.entries(filters).forEach(([key, value]) => {
          if (value) queryParams.append(key, value);
        });

        const url = `/api/animals/?${queryParams.toString()}`;
        console.log("Fetching:", url);

        const response = await fetch(url, {
          credentials: "include",
        });

        if (!response.ok) throw new Error('Failed to fetch animals');
        const data = await response.json();

        if (Array.isArray(data)) {
          setAnimals(data);
        } else {
          console.warn('Unexpected format:', data);
          setAnimals([]);
        }

        setError(null);
      } catch (err) {
        console.error('Error fetching animals:', err);
        setError('Failed to load animals.');
        setAnimals([]);
      } finally {
        setLoading(false);
      }
    };


    fetchAnimals();
  }, [filters]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      species: '',
      gender: '',
      age_min: '',
      age_max: '',
      size: '',
      energy_level: ''
    });
  };

  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="hero-content">
          <h1>Available Animals</h1>
        </div>
      </div>

      <div className="animals-section">
        <div className="section-header">
          <h2>Available Animals</h2>
          <div className="filter-controls">
            <div className="filter-form">
              <div className="filter-group">
                <label htmlFor="species">Animal Type</label>
                <select id="species" name="species" value={filters.species} onChange={handleFilterChange}>
                  <option value="">All Types</option>
                  <option value="Dog">Dogs</option>
                  <option value="Cat">Cats</option>
                  <option value="Small Animal">Small Animals</option>
                  <option value="Bird">Birds</option>
                  <option value="Reptile">Reptiles</option>
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="size">Size</label>
                <select id="size" name="size" value={filters.size} onChange={handleFilterChange}>
                  <option value="">Any Size</option>
                  <option value="Small">Small</option>
                  <option value="Medium">Medium</option>
                  <option value="Large">Large</option>
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="energy_level">Energy Level</label>
                <select id="energy_level" name="energy_level" value={filters.energy_level} onChange={handleFilterChange}>
                  <option value="">Any Energy Level</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>

              <button onClick={clearFilters} className="clear-filters-button">
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="animals-loading">
            <div className="loading-spinner"></div>
            <p>Loading animals...</p>
          </div>
        ) : error ? (
          <div className="animals-error">
            <p>{error}</p>
            <button onClick={() => window.location.reload()} className="retry-button">
              Try Again
            </button>
          </div>
        ) : animals.length > 0 ? (
          <div className="animals-grid">
            {animals.map(animal => (
              <Link key={animal.id} to={`/animals/${animal.id}`} className="animal-card">
                <div className="animal-card-image">
                  <img src={getBreedImageUrl(animal)} alt={animal.name} />
                </div>
                <div className="animal-card-content">
                  <h3>{animal.name}</h3>
                  <p className="animal-breed">{animal.breed || 'Unknown Breed'}</p>
                  <p className="animal-age">
                    {animal.age_years || animal.age_months
                      ? `${animal.age_years || 0}y ${animal.age_months || 0}m`
                      : 'Age unknown'}
                  </p>
                  <p className="animal-location">{animal.shelter?.city || 'Unknown Location'}</p>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="no-animals">
            <p>No animals found matching your filters.</p>
            <button onClick={clearFilters} className="clear-filters-button">
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Animals;
