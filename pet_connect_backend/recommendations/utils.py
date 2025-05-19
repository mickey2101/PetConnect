# recommendations/utils.py
import numpy as np
from users.models import UserProfile
from animals.models import Animal
from .models import AnimalRecommendation

def calculate_compatibility_score(user_profile, animal):
    """
    Calculate a compatibility score between a user profile and an animal
    Returns a score between 0 and 1, where 1 is a perfect match
    """
    score = 1.0  # Start with a perfect score and reduce based on incompatibilities
    
    # Check essential compatibility factors (deal breakers)
    # If the user has children but the animal is not good with kids, major penalty
    if user_profile.has_children and not animal.good_with_kids:
        score *= 0.3
    
    # If the user has other dogs but the animal is not good with dogs, major penalty
    if user_profile.has_other_dogs and not animal.good_with_dogs:
        score *= 0.3
    
    # If the user has other cats but the animal is not good with cats, major penalty
    if user_profile.has_other_cats and not animal.good_with_cats:
        score *= 0.3
    
    # Check animal type preference
    if user_profile.preferred_animal_type and animal.species != user_profile.preferred_animal_type:
        score *= 0.5
    
    # Check age preference (normalized penalty based on how far outside the range)
    age_in_months = (animal.age_years * 12) + animal.age_months
    if age_in_months < user_profile.preferred_age_min:
        # Too young
        diff = user_profile.preferred_age_min - age_in_months
        penalty = min(0.5, diff / 12 * 0.1)  # 10% penalty per year too young, max 50%
        score *= (1 - penalty)
    elif age_in_months > user_profile.preferred_age_max:
        # Too old
        diff = age_in_months - user_profile.preferred_age_max
        penalty = min(0.5, diff / 12 * 0.1)  # 10% penalty per year too old, max 50%
        score *= (1 - penalty)
    
    # Optional: Add more sophisticated compatibility calculations here
    
    # Ensure the score is between 0 and 1
    return max(0.1, min(score, 1.0))

def update_recommendations_for_user(user):
    """
    Update all recommendation scores for a user
    This should be called whenever a user's preferences change
    """
    try:
        user_profile = UserProfile.objects.get(user=user)
        
        # Get all available animals
        available_animals = Animal.objects.filter(status='A')
        
        # Calculate and store scores
        for animal in available_animals:
            score = calculate_compatibility_score(user_profile, animal)
            
            # Update or create recommendation score
            AnimalRecommendation.objects.update_or_create(
                user=user,
                animal=animal,
                defaults={'score': score}
            )
        
        return True
    except Exception as e:
        print(f"Error updating recommendations: {e}")
        return False

def get_recommendations_for_user(user, limit=10):
    """
    Get the top recommendations for a user
    """
    # Update recommendations first to ensure they're current
    update_recommendations_for_user(user)
    
    # Return the top recommendations
    return AnimalRecommendation.objects.filter(user=user).order_by('-score')[:limit]