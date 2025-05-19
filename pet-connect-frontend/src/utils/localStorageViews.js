/**
 * Local Storage based animal view tracking
 * Used as fallback when the API endpoints aren't working
 */

// Key for storing views in localStorage
const ANIMAL_VIEWS_KEY = 'pet_connect_animal_views';

/**
 * Log an animal view to localStorage
 * @param {number} animalId - ID of the viewed animal
 * @param {Object} animalData - Optional animal data to store
 */
export const logLocalAnimalView = (animalId, animalData = {}) => {
  try {
    // Get existing views
    const existingViews = getLocalAnimalViews();
    
    // Create a new view record
    const newView = {
      animalId: parseInt(animalId),
      timestamp: new Date().toISOString(),
      data: animalData
    };
    
    // Add to the beginning of the array (most recent first)
    existingViews.unshift(newView);
    
    // Limit to 50 most recent views to avoid storage issues
    const limitedViews = existingViews.slice(0, 50);
    
    // Save back to localStorage
    localStorage.setItem(ANIMAL_VIEWS_KEY, JSON.stringify(limitedViews));
    
    console.log(`Locally logged view for animal ${animalId}`);
    return true;
  } catch (error) {
    console.error('Error logging view to localStorage:', error);
    return false;
  }
};

/**
 * Get all locally stored animal views
 * @returns {Array} Array of view objects
 */
export const getLocalAnimalViews = () => {
  try {
    const storedViews = localStorage.getItem(ANIMAL_VIEWS_KEY);
    return storedViews ? JSON.parse(storedViews) : [];
  } catch (error) {
    console.error('Error retrieving views from localStorage:', error);
    return [];
  }
};

/**
 * Get recently viewed animal IDs
 * @param {number} limit - Maximum number of views to return
 * @returns {Array} Array of animal IDs
 */
export const getRecentlyViewedAnimalIds = (limit = 5) => {
  const views = getLocalAnimalViews();
  // Get unique animal IDs (most recent first)
  const uniqueIds = [...new Set(views.map(view => view.animalId))];
  return uniqueIds.slice(0, limit);
};

/**
 * Check if an animal has been viewed
 * @param {number} animalId - ID of the animal to check
 * @returns {boolean} True if the animal has been viewed
 */
export const hasViewedAnimal = (animalId) => {
  const views = getLocalAnimalViews();
  return views.some(view => view.animalId === parseInt(animalId));
};

/**
 * Clear all locally stored animal views
 * @returns {boolean} Success status
 */
export const clearLocalAnimalViews = () => {
  try {
    localStorage.removeItem(ANIMAL_VIEWS_KEY);
    console.log('Cleared all local animal views');
    return true;
  } catch (error) {
    console.error('Error clearing local animal views:', error);
    return false;
  }
};

/**
 * Calculate similarity score between animals
 * @param {Object} animal1 - First animal to compare
 * @param {Object} animal2 - Second animal to compare
 * @returns {number} Similarity score between 0-1
 */
export const calculateSimilarity = (animal1, animal2) => {
  if (!animal1 || !animal2) return 0;
  
  let score = 0;
  let maxScore = 0;
  
  // Species match (highest weight)
  maxScore += 3;
  if (animal1.species === animal2.species) {
    score += 3;
  }
  
  // Breed match
  maxScore += 2;
  if (animal1.breed && animal2.breed && animal1.breed === animal2.breed) {
    score += 2;
  }
  
  // Size match
  maxScore += 1;
  if (animal1.size && animal2.size && animal1.size === animal2.size) {
    score += 1;
  }
  
  // Age similarity
  maxScore += 1;
  const age1 = (animal1.age_years || 0) + (animal1.age_months || 0) / 12;
  const age2 = (animal2.age_years || 0) + (animal2.age_months || 0) / 12;
  const ageDiff = Math.abs(age1 - age2);
  if (ageDiff < 2) {
    score += 1;
  }
  
  // Return normalized score
  return maxScore > 0 ? score / maxScore : 0;
};

/**
 * Get client-side recommendations based on view history and available animals
 * @param {Array} viewedAnimals - Animals the user has viewed
 * @param {Array} availableAnimals - All available animals to choose from
 * @param {number} limit - Maximum recommendations to return
 * @returns {Array} Recommended animals
 */
export const getClientRecommendations = (viewedAnimals, availableAnimals, limit = 10) => {
  if (!viewedAnimals || viewedAnimals.length === 0 || !availableAnimals || availableAnimals.length === 0) {
    return [];
  }
  
  console.log("Building client recommendations from:", 
    viewedAnimals.map(a => `${a.name} (${a.species})`));
  
  // Get IDs of viewed animals
  const viewedIds = viewedAnimals.map(animal => animal.id);
  
  // First, identify species the user has viewed
  const viewedSpecies = new Set(viewedAnimals.map(animal => animal.species));
  console.log("User has viewed species:", Array.from(viewedSpecies));
  
  // Filter available animals to prioritize same species first
  const sameSpeciesAnimals = availableAnimals.filter(animal => 
    viewedSpecies.has(animal.species) && !viewedIds.includes(animal.id)
  );
  
  console.log(`Found ${sameSpeciesAnimals.length} available animals matching viewed species`);
  
  // If we don't have enough same-species animals, add some others
  let recommendations = [...sameSpeciesAnimals];
  
  if (recommendations.length < limit) {
    // Get other animals not of the viewed species
    const otherAnimals = availableAnimals.filter(animal => 
      !viewedSpecies.has(animal.species) && !viewedIds.includes(animal.id)
    );
    
    // Add enough to reach the limit
    recommendations = [
      ...recommendations,
      ...otherAnimals.slice(0, limit - recommendations.length)
    ];
  }
  
  // Limit to requested amount and add reasons
  const finalRecs = recommendations.slice(0, limit).map(animal => {
    // Add similarity score based on species match
    const similarityScore = viewedSpecies.has(animal.species) ? 0.9 : 0.3;
    
    // Get the reason based on whether it matches viewed species
    const reason = viewedSpecies.has(animal.species)
      ? `Similar to ${animal.species.toLowerCase()}s you've viewed` 
      : 'You might also like';
    
    return {
      ...animal,
      recommendation_reason: reason,
      similarity_score: similarityScore,
      client_recommendation: true
    };
  });
  
  console.log("Final client recommendations:", 
    finalRecs.map(r => `${r.name} (${r.species}, score: ${r.similarity_score})`));
  
  return finalRecs;
};

// Create a named object before exporting
const localStorageViewsService = {
  logLocalAnimalView,
  getLocalAnimalViews,
  getRecentlyViewedAnimalIds,
  hasViewedAnimal,
  clearLocalAnimalViews,
  calculateSimilarity,
  getClientRecommendations
};

export default localStorageViewsService;