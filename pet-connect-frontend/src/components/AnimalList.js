// src/components/AnimalList.js
import React from 'react';
import { Link } from 'react-router-dom';

function AnimalList({ animals }) {
  console.log('AnimalList received animals:', animals);
  
  if (!animals || animals.length === 0) {
    return (
      <div className="container mx-auto p-4 text-center">
        <p>No animals available for adoption at this time.</p>
        <p className="text-sm text-gray-600">Debug info: Received {Array.isArray(animals) ? animals.length : 'non-array'} animals</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {animals.map((animal, index) => {
          console.log(`Rendering animal ${index}:`, animal);
          return (
            <div key={animal.id || index} className="border rounded-lg p-4 shadow-md">
              <h2 className="text-xl font-semibold">{animal.name}</h2>
              <p className="text-gray-600">{animal.species} - {animal.breed}</p>
              <p>
                Age: {animal.age_years > 0 ? `${animal.age_years} years` : ''} 
                {animal.age_months > 0 ? ` ${animal.age_months} months` : ''}
              </p>
              <p>Gender: {animal.gender === 'M' ? 'Male' : animal.gender === 'F' ? 'Female' : 'Unknown'}</p>
              <div className="mt-2 text-sm">
                <p>{animal.good_with_kids ? '✓' : '✗'} Good with kids</p>
                <p>{animal.good_with_cats ? '✓' : '✗'} Good with cats</p>
                <p>{animal.good_with_dogs ? '✓' : '✗'} Good with dogs</p>
              </div>
              <div className="mt-4">
                <Link 
                  to={`/animals/${animal.id}`}
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  View Details
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default AnimalList;