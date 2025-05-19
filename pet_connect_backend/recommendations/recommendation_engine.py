# recommendations/recommendation_engine.py

import numpy as np
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Set up logging
logger = logging.getLogger(__name__)

class MLRecommendationEngine:
    """
    An enhanced recommendation engine for Pet Connect that combines:
    1. User preference-based filtering (from existing preferences)
    2. View history analysis (using machine learning techniques)
    3. Content-based similarity analysis
    """
    
    def __init__(self):
        # Recommendation weights
        self.preference_weight = 0.8    # Weight for explicit preferences
        self.view_history_weight = 0.3  # Weight for viewing history patterns
        self.similarity_weight = 0.2    # Weight for content similarity
        
        # Adaptation settings
        self.min_views = 2              # Minimum views before using view history
        self.recency_days = 14          # Days to consider for recency weighting
        self.recency_decay = 0.9        # Daily decay factor for view importance
    
    def get_recommendations(self, user_id, limit=10):
        """Get personalized animal recommendations using ML techniques"""
        from django.contrib.auth.models import User
        from animals.models import Animal, AnimalViewHistory
        from users.models import UserProfile
        
        try:
            # Get user data
            user = User.objects.get(id=user_id)
            
            # Log the recommendation request
            logger.info(f"Getting ML recommendations for user {user.username} (id: {user_id})")
            
            # Get all available animals
            all_animals = Animal.objects.filter(status='A')
            
            # If no animals are available, return empty list
            if not all_animals.exists():
                logger.warning("No available animals found")
                return []
            
            # Get user profile for preference-based recommendations
            profile = UserProfile.objects.filter(user=user).first()
            
            # Get user view history
            view_history = AnimalViewHistory.objects.filter(user=user).order_by('-timestamp')
            viewed_animal_ids = list(view_history.values_list('animal_id', flat=True))
            
            # Log view history stats
            logger.info(f"User has viewed {len(viewed_animal_ids)} animals")
            
            # Build candidate pool (excluding recently viewed animals)
            candidates = all_animals
            if viewed_animal_ids:
                # Don't exclude all viewed animals, just the 3 most recently viewed
                recent_views = viewed_animal_ids[:3]
                candidates = all_animals.exclude(id__in=recent_views)
            
            # Initialize scores dictionary
            animal_scores = {}
            
            # 1. Score based on user preferences
            if profile:
                preference_scores = self._score_by_preferences(candidates, profile)
                for animal_id, score in preference_scores.items():
                    if animal_id not in animal_scores:
                        animal_scores[animal_id] = 0
                    animal_scores[animal_id] += score * self.preference_weight
            
            # 2. Score based on view history patterns (if enough views)
            if view_history.count() >= self.min_views:
                view_history_scores = self._score_by_view_history(candidates, view_history)
                for animal_id, score in view_history_scores.items():
                    if animal_id not in animal_scores:
                        animal_scores[animal_id] = 0
                    animal_scores[animal_id] += score * self.view_history_weight
            
            # 3. Score based on content similarity to viewed animals
            if view_history.exists():
                similarity_scores = self._score_by_content_similarity(candidates, view_history)
                for animal_id, score in similarity_scores.items():
                    if animal_id not in animal_scores:
                        animal_scores[animal_id] = 0
                    animal_scores[animal_id] += score * self.similarity_weight
            
            # If we have no scores (no preferences, no history), return popular animals
            if not animal_scores:
                logger.info("No personalization possible, using popular animals")
                popular_animals = self._get_popular_animals(limit)
                return popular_animals
            
            # Sort animals by final score and return IDs
            sorted_animals = sorted(animal_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Log top scoring animals
            logger.info(f"Top scoring animals: {sorted_animals[:min(3, len(sorted_animals))]}")
            
            recommended_ids = [animal_id for animal_id, _ in sorted_animals[:limit]]
            
            # If we don't have enough recommendations, add popular animals
            if len(recommended_ids) < limit:
                remaining = limit - len(recommended_ids)
                logger.info(f"Only {len(recommended_ids)} scored animals, adding {remaining} popular animals")
                
                popular_animals = self._get_popular_animals(
                    remaining, 
                    exclude_ids=recommended_ids + viewed_animal_ids[:5]
                )
                recommended_ids.extend(popular_animals)
            
            logger.info(f"Returning {len(recommended_ids)} recommendations")
            return recommended_ids
            
        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def _score_by_preferences(self, candidates, profile):
        """Score animals based on user preferences from profile"""
        scores = {}
        small_animals = ['Hamster', 'Guinea Pig', 'Rabbit', 'Gerbil', 'Mouse', 'Rat', 'Ferret']
        
        # Log preferences for debugging
        logger.info(f"Scoring with preferences - Species: {profile.preferred_species}, "
                   f"Size: {profile.preferred_size}, Age: {profile.preferred_age_min}-{profile.preferred_age_max}")
        
        for animal in candidates:
            score = 0
            max_score = 0
            matches = []
            
            # Species preference (highest weight)
            if profile.preferred_species:
                max_score += 4
                
                # Handle 'Small Animal' preference
                if profile.preferred_species == 'Small Animal' and animal.species in small_animals:
                    score += 4
                    matches.append(f"small animal ({animal.species})")
                elif animal.species == profile.preferred_species:
                    score += 4
                    matches.append(f"species ({animal.species})")
            
            # Size preference
            if profile.preferred_size and hasattr(animal, 'size'):
                max_score += 2
                if animal.size == profile.preferred_size:
                    score += 2
                    matches.append(f"size ({animal.size})")
            
            # Age preference
            if hasattr(profile, 'preferred_age_min') and hasattr(profile, 'preferred_age_max'):
                max_score += 2
                age_in_years = animal.age_years
                if hasattr(animal, 'age_months'):
                    age_in_years += animal.age_months / 12
                
                if profile.preferred_age_min <= age_in_years <= profile.preferred_age_max:
                    score += 2
                    matches.append(f"age ({age_in_years:.1f} years)")
            
            # Energy level preference
            if profile.preferred_energy_level and hasattr(animal, 'energy_level'):
                max_score += 2
                if animal.energy_level == profile.preferred_energy_level:
                    score += 2
                    matches.append(f"energy ({animal.energy_level})")
            
            # Good with children preference
            if profile.good_with_children and hasattr(animal, 'good_with_kids'):
                max_score += 1
                if animal.good_with_kids:
                    score += 1
                    matches.append("good with children")
            
            # Good with other pets preference
            if profile.good_with_other_pets:
                max_score += 1
                if (hasattr(animal, 'good_with_cats') and animal.good_with_cats) or \
                   (hasattr(animal, 'good_with_dogs') and animal.good_with_dogs):
                    score += 1
                    matches.append("good with other pets")
            
            # Normalize score (0-1)
            if max_score > 0:
                normalized_score = score / max_score
            else:
                normalized_score = 0
            
            scores[animal.id] = normalized_score
            
            # Log high matching scores for debugging
            if normalized_score > 0.7:
                logger.debug(f"Animal {animal.id} ({animal.name}) scored {normalized_score:.2f} for preferences. Matches: {', '.join(matches)}")
        
        return scores
    
    def _score_by_view_history(self, candidates, view_history):
        """Score animals based on patterns in user viewing history"""
        scores = {}
        
        # Count how many times each species/breed/characteristic has been viewed
        species_counts = {}
        breed_counts = {}
        size_counts = {}
        feature_counts = {}
        
        # Apply recency weighting to views
        now = timezone.now()
        
        for view in view_history:
            animal = view.animal
            
            # Calculate recency weight
            days_ago = (now - view.timestamp).days
            recency_weight = self.recency_decay ** min(days_ago, self.recency_days)
            
            # Count species views with recency weighting
            species = animal.species
            if species not in species_counts:
                species_counts[species] = 0
            species_counts[species] += recency_weight
            
            # Count breed views with recency weighting
            if hasattr(animal, 'breed') and animal.breed:
                breed = animal.breed
                if breed not in breed_counts:
                    breed_counts[breed] = 0
                breed_counts[breed] += recency_weight
            
            # Count size views with recency weighting
            if hasattr(animal, 'size') and animal.size:
                size = animal.size
                if size not in size_counts:
                    size_counts[size] = 0
                size_counts[size] += recency_weight
            
            # Count feature views with recency weighting
            for feature in ['good_with_kids', 'good_with_cats', 'good_with_dogs', 'energy_level']:
                if hasattr(animal, feature):
                    value = getattr(animal, feature)
                    if value:  # Only count True boolean values or non-empty strings
                        feature_key = f"{feature}_{value}"
                        if feature_key not in feature_counts:
                            feature_counts[feature_key] = 0
                        feature_counts[feature_key] += recency_weight
        
        # Normalize counts to get probabilities
        total_views = sum(species_counts.values())
        if total_views > 0:
            for species in species_counts:
                species_counts[species] /= total_views
            
            for breed in breed_counts:
                breed_counts[breed] /= total_views
            
            for size in size_counts:
                size_counts[size] /= total_views
            
            for feature in feature_counts:
                feature_counts[feature] /= total_views
        
        # Log view patterns
        logger.debug(f"Species viewing pattern: {dict(species_counts)}")
        
        # Score each candidate animal based on viewing patterns
        for animal in candidates:
            score = 0
            
            # Score based on species
            species = animal.species
            if species in species_counts:
                score += species_counts[species] * 0.4  # 40% weight to species
            
            # Score based on breed
            if hasattr(animal, 'breed') and animal.breed and animal.breed in breed_counts:
                score += breed_counts[animal.breed] * 0.3  # 30% weight to breed
            
            # Score based on size
            if hasattr(animal, 'size') and animal.size and animal.size in size_counts:
                score += size_counts[animal.size] * 0.2  # 20% weight to size
            
            # Score based on features
            for feature in ['good_with_kids', 'good_with_cats', 'good_with_dogs', 'energy_level']:
                if hasattr(animal, feature):
                    value = getattr(animal, feature)
                    if value:
                        feature_key = f"{feature}_{value}"
                        if feature_key in feature_counts:
                            score += feature_counts[feature_key] * 0.1 / 4  # 10% weight split among features
            
            scores[animal.id] = score
        
        return scores
    
    def _score_by_content_similarity(self, candidates, view_history):
        """Score animals based on content similarity to viewed animals"""
        from animals.models import Animal
        
        # Get the animals user has viewed
        viewed_animal_ids = view_history.values_list('animal_id', flat=True)
        viewed_animals = Animal.objects.filter(id__in=viewed_animal_ids)
        
        if not viewed_animals.exists():
            return {}
        
        # Create feature vectors for all animals (viewed + candidates)
        all_animals = list(viewed_animals) + list(candidates)
        
        # Create feature vectors
        features = []
        for animal in all_animals:
            # Create a combined text feature
            text_features = []
            
            # Add species as a feature
            if hasattr(animal, 'species'):
                text_features.append(f"species_{animal.species}")
            
            # Add breed as a feature
            if hasattr(animal, 'breed') and animal.breed:
                text_features.append(f"breed_{animal.breed}")
            
            # Add size as a feature
            if hasattr(animal, 'size') and animal.size:
                text_features.append(f"size_{animal.size}")
            
            # Add age as a feature
            age_in_years = animal.age_years
            if hasattr(animal, 'age_months'):
                age_in_years += animal.age_months / 12
            
            age_category = "young" if age_in_years < 2 else "adult" if age_in_years < 8 else "senior"
            text_features.append(f"age_{age_category}")
            
            # Add energy level as a feature
            if hasattr(animal, 'energy_level') and animal.energy_level:
                text_features.append(f"energy_{animal.energy_level}")
            
            # Add compatibility features
            for field in ['good_with_kids', 'good_with_cats', 'good_with_dogs']:
                if hasattr(animal, field) and getattr(animal, field):
                    text_features.append(field)
            
            features.append(" ".join(text_features))
        
        try:
            # Use TF-IDF to vectorize features
            vectorizer = TfidfVectorizer()
            feature_matrix = vectorizer.fit_transform(features)
            
            # Calculate similarity between viewed animals and candidates
            viewed_indices = list(range(len(viewed_animals)))
            candidate_indices = list(range(len(viewed_animals), len(all_animals)))
            
            # Calculate similarity scores
            similarity_scores = {}
            
            for cand_idx in candidate_indices:
                cand_vector = feature_matrix[cand_idx]
                
                # Calculate average similarity to viewed animals
                total_sim = 0
                for viewed_idx in viewed_indices:
                    viewed_vector = feature_matrix[viewed_idx]
                    sim = cosine_similarity(cand_vector, viewed_vector)[0][0]
                    total_sim += sim
                
                avg_sim = total_sim / len(viewed_indices) if viewed_indices else 0
                animal_id = all_animals[cand_idx].id
                similarity_scores[animal_id] = avg_sim
            
            return similarity_scores
            
        except Exception as e:
            logger.error(f"Error calculating content similarity: {str(e)}")
            return {}
    
    def _get_popular_animals(self, limit, exclude_ids=None):
        """Get popular animals based on view count"""
        from animals.models import Animal, AnimalViewHistory
        from django.db.models import Count
        
        query = Animal.objects.filter(status='A')
        
        if exclude_ids:
            query = query.exclude(id__in=exclude_ids)
        
        # Get animals with most views
        popular = query.annotate(
            view_count=Count('animalviewhistory')
        ).order_by('-view_count')
        
        # If no views exist, return random animals
        if not popular.exists() or popular.first().view_count == 0:
            logger.info("No view data available, using random selection for popular animals")
            return list(query.order_by('?')[:limit].values_list('id', flat=True))
        
        return list(popular[:limit].values_list('id', flat=True))
    
    def get_recommendation_reason(self, user_id, animal):
        """Generate a personalized reason for a recommendation"""
        from django.contrib.auth.models import User
        from users.models import UserProfile
        from animals.models import AnimalViewHistory
        
        try:
            user = User.objects.get(id=user_id)
            
            # Check for previous interactions with this animal
            previous_views = AnimalViewHistory.objects.filter(user=user, animal=animal).count()
            if previous_views > 0:
                return f"Similar to animals you've viewed before"
            
            # Get user preferences
            user_pref = UserProfile.objects.filter(user=user).first()
            
            if user_pref:
                # Check if the animal matches species preference
                if hasattr(user_pref, 'preferred_species') and user_pref.preferred_species:
                    # Handle Small Animal special case
                    if user_pref.preferred_species == 'Small Animal':
                        small_animals = ['Hamster', 'Guinea Pig', 'Rabbit', 'Gerbil', 'Mouse', 'Rat', 'Ferret']
                        if hasattr(animal, 'species') and animal.species in small_animals:
                            return f"Matches your preference for small animals"
                    
                    # Regular species matching
                    elif hasattr(animal, 'species') and animal.species == user_pref.preferred_species:
                        return f"Matches your {animal.species.lower()} preference"
                
                # Check size preference
                if hasattr(user_pref, 'preferred_size') and hasattr(animal, 'size'):
                    if user_pref.preferred_size == animal.size:
                        return f"Matches your preference for {animal.size.lower()} sized pets"
                
                # Check energy level preference
                if hasattr(user_pref, 'preferred_energy_level') and hasattr(animal, 'energy_level'):
                    if user_pref.preferred_energy_level == animal.energy_level:
                        return f"Matches your preference for {animal.energy_level.lower()} energy pets"
                
                # Check age preference
                if (hasattr(user_pref, 'preferred_age_min') and 
                    hasattr(user_pref, 'preferred_age_max') and
                    hasattr(animal, 'age_years')):
                    age_in_years = animal.age_years
                    if hasattr(animal, 'age_months'):
                        age_in_years += animal.age_months / 12
                    
                    if user_pref.preferred_age_min <= age_in_years <= user_pref.preferred_age_max:
                        if age_in_years < 2:
                            return "Young pet within your preferred age range"
                        elif age_in_years < 8:
                            return "Adult pet within your preferred age range"
                        else:
                            return "Senior pet within your preferred age range"
                
                # Check compatibility preferences
                if hasattr(user_pref, 'good_with_children') and user_pref.good_with_children:
                    if hasattr(animal, 'good_with_kids') and animal.good_with_kids:
                        return "Great with children"
                
                if hasattr(user_pref, 'good_with_other_pets') and user_pref.good_with_other_pets:
                    if (hasattr(animal, 'good_with_cats') and animal.good_with_cats) or \
                       (hasattr(animal, 'good_with_dogs') and animal.good_with_dogs):
                        return "Gets along well with other pets"
            
            # Check user view history for patterns
            view_history = AnimalViewHistory.objects.filter(user=user).exclude(animal=animal)
            
            if view_history.exists():
                # Check if user has viewed animals of the same species
                same_species_views = view_history.filter(animal__species=animal.species).count()
                if same_species_views > 0:
                    return f"Similar to {animal.species.lower()}s you've viewed"
                
                # Check if user has viewed animals of the same breed
                if hasattr(animal, 'breed') and animal.breed:
                    same_breed_views = view_history.filter(animal__breed=animal.breed).count()
                    if same_breed_views > 0:
                        return f"Similar breed to animals you've viewed"
            
            # Default species-based reasons
            if hasattr(animal, 'species'):
                if animal.species == "Dog":
                    return "Loyal and friendly companion"
                elif animal.species == "Cat":
                    return "Independent and affectionate pet"
                elif animal.species == "Rabbit":
                    return "Adorable and low-maintenance pet"
                elif animal.species == "Guinea Pig":
                    return "Sociable and gentle pet"
                elif animal.species == "Hamster":
                    return "Compact and entertaining companion"
                else:
                    return "Wonderful pet looking for a home"
                    
        except User.DoesNotExist:
            return "Popular pet ready for adoption"
        except Exception as e:
            logger.error(f"Error generating recommendation reason: {str(e)}")
            return "Recommended based on availability"