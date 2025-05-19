"""
Pet Connect - Recommendation Tests
--------------------------------
Test cases for the recommendation engine and views.

Author: Macayla van der Merwe
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from animals.models import Animal, AnimalViewHistory
from users.models import UserProfile
from recommendations.models import AnimalRecommendation
from recommendations.recommendation_engine import PetConnectRecommendationEngine

class RecommendationEngineTests(TestCase):
    """Test cases for the recommendation engine"""
    
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='password123')
        
        # Create user profiles
        self.profile1 = UserProfile.objects.get(user=self.user1)
        self.profile1.preferred_species = 'Dog'
        self.profile1.preferred_age_min = 1
        self.profile1.preferred_age_max = 5
        self.profile1.save()
        
        self.profile2 = UserProfile.objects.get(user=self.user2)
        self.profile2.preferred_species = 'Cat'
        self.profile2.save()
        
        # Create test animals
        self.dog1 = Animal.objects.create(
            name='Max', 
            species='Dog', 
            breed='Labrador',
            age_years=3,
            gender='Male',
            good_with_children=True
        )
        
        self.dog2 = Animal.objects.create(
            name='Buddy', 
            species='Dog', 
            breed='Beagle',
            age_years=2,
            gender='Male',
            good_with_children=False
        )
        
        self.cat1 = Animal.objects.create(
            name='Whiskers', 
            species='Cat', 
            breed='Siamese',
            age_years=4,
            gender='Female',
            good_with_children=True
        )
        
        # Initialize recommendation engine
        self.engine = PetConnectRecommendationEngine()
    
    def test_get_recommendations_without_history(self):
        """Test getting recommendations without any viewing history"""
        # Get recommendations for user1 who prefers dogs
        recommendations = self.engine.get_recommendations(self.user1.id, limit=5)
        
        # Should recommend dogs since user1 prefers dogs
        self.assertIn(self.dog1.id, recommendations)
        self.assertIn(self.dog2.id, recommendations)
        
        # Get recommendations for user2 who prefers cats
        recommendations = self.engine.get_recommendations(self.user2.id, limit=5)
        
        # Should recommend cats since user2 prefers cats
        self.assertIn(self.cat1.id, recommendations)
    
    def test_update_recommendations_from_view(self):
        """Test updating recommendations after a user views an animal"""
        # User1 views a cat (different from preference)
        self.engine.update_recommendations_from_view(
            user_id=self.user1.id,
            animal_id=self.cat1.id,
            view_duration=60
        )
        
        # Check if recommendation was created
        rec = AnimalRecommendation.objects.filter(
            user=self.user1,
            animal=self.cat1
        ).first()
        
        self.assertIsNotNone(rec)
        self.assertTrue(rec.interaction_score > 0)
        
        # Get updated recommendations
        recommendations = self.engine.get_recommendations(self.user1.id, limit=5)
        
        # Should still include the cat that was viewed
        self.assertIn(self.cat1.id, recommendations)
    
    def test_recommendation_reason_generation(self):
        """Test generation of personalized recommendation reasons"""
        # User1 views a dog
        AnimalViewHistory.objects.create(
            user=self.user1,
            animal=self.dog1,
            species=self.dog1.species
        )
        
        # Test reason for a similar dog
        reason = self.engine._generate_recommendation_reason(self.user1, self.dog2)
        
        # Should mention either preference or similarity
        self.assertTrue(
            "preference" in reason.lower() or 
            "similar" in reason.lower()
        )
        
        # Test reason for a cat (different species)
        reason = self.engine._generate_recommendation_reason(self.user1, self.cat1)
        
        # Should be a general reason for cats
        self.assertTrue(
            "independent" in reason.lower() or
            "affectionate" in reason.lower() or
            "children" in reason.lower()
        )


class RecommendationAPITests(TestCase):
    """Test cases for the recommendation API"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Create user profile
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.preferred_species = 'Dog'
        self.profile.save()
        
        # Create test animals
        self.dog = Animal.objects.create(
            name='Max', 
            species='Dog', 
            breed='Labrador',
            age_years=3,
            gender='Male'
        )
        
        self.cat = Animal.objects.create(
            name='Whiskers', 
            species='Cat', 
            breed='Siamese',
            age_years=4,
            gender='Female'
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_recommendations(self):
        """Test getting recommendations via API"""
        response = self.client.get('/api/recommendations/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('recommendations', response.data)
        
        # First recommendation should be a dog based on preferences
        if response.data['recommendations']:
            first_rec = response.data['recommendations'][0]
            self.assertEqual(first_rec['species'], 'Dog')
    
    def test_record_view(self):
        """Test recording a view via API"""
        response = self.client.post(f'/api/recommendations/{self.cat.id}/record_view/', {
            'duration': 30
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'view recorded')
        
        # Check if view was recorded
        view = AnimalViewHistory.objects.filter(
            user=self.user,
            animal=self.cat
        ).first()
        
        self.assertIsNotNone(view)
        self.assertEqual(view.view_duration, 30)
        
        # Check if recommendation was created
        rec = AnimalRecommendation.objects.filter(
            user=self.user,
            animal=self.cat
        ).first()
        
        self.assertIsNotNone(rec)
        self.assertTrue(rec.interaction_score > 0)
    
    def test_recent_views(self):
        """Test getting recent views via API"""
        # Create some views
        AnimalViewHistory.objects.create(
            user=self.user,
            animal=self.dog,
            species=self.dog.species
        )
        
        AnimalViewHistory.objects.create(
            user=self.user,
            animal=self.cat,
            species=self.cat.species
        )
        
        response = self.client.get('/api/recommendations/recent_views/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('recent_views', response.data)
        self.assertEqual(len(response.data['recent_views']), 2)