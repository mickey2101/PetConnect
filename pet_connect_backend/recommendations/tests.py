"""
Pet Connect - Tests for Recommendation Engine
--------------------------------------------
Unit tests for the recommendation engine components.

Author: Macayla van der Merwe
"""

import unittest
from unittest import mock
import pandas as pd
import numpy as np
import os
import tempfile
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from pets.models import Pet, Shelter, UserPreference, UserViewHistory, PetRecommendation
from pets.recommendation_engine import HybridRecommendationEngine
from pets.views import get_user_recommendations, log_pet_view


class ContentBasedRecommendationTests(unittest.TestCase):
    """Test content-based filtering recommendations."""
    
    def setUp(self):
        """Set up test data."""
        # Create a temporary directory for model files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create the recommendation engine
        self.engine = HybridRecommendationEngine(model_dir=self.temp_dir)
        
        # Create sample pet data
        self.pet_data = pd.DataFrame({
            'id': range(1, 11),
            'name': [f'Pet{i}' for i in range(1, 11)],
            'species': ['Dog', 'Dog', 'Dog', 'Cat', 'Cat', 'Cat', 'Small Animal', 'Small Animal', 'Bird', 'Reptile'],
            'breed': ['Labrador', 'Labrador', 'Poodle', 'Siamese', 'Siamese', 'Persian', 'Hamster', 'Guinea Pig', 'Canary', 'Gecko'],
            'age': [2, 3, 5, 1, 2, 4, 1, 2, 1, 3],
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
            'size': ['Large', 'Large', 'Medium', 'Small', 'Small', 'Medium', 'Small', 'Small', 'Small', 'Small'],
            'energy_level': ['High', 'High', 'Medium', 'Low', 'Medium', 'Low', 'High', 'Medium', 'Medium', 'Low'],
            'health_status': ['Healthy'] * 10,
            'behavior_traits': [
                'Friendly, Playful, Good with children',
                'Friendly, Playful, Good with other dogs',
                'Friendly, Calm, Good with children',
                'Independent, Calm, Good with other cats',
                'Friendly, Playful, Good with children',
                'Independent, Calm',
                'Active, Nocturnal',
                'Friendly, Social',
                'Vocal, Active',
                'Calm, Easy to care for'
            ],
            'description': [
                'A friendly Labrador who loves to play fetch.',
                'A playful Labrador who gets along well with other dogs.',
                'A calm Poodle who is great with kids.',
                'A calm Siamese cat who likes to be independent.',
                'A playful Siamese cat who loves attention.',
                'A calm Persian cat who prefers to be alone.',
                'An active hamster who is mainly active at night.',
                'A friendly guinea pig who enjoys socializing.',
                'A vocal canary who sings beautifully.',
                'A calm gecko who is easy to take care of.'
            ]
        })
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory and all files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_content_model_training(self):
        """Test that the content-based model can be trained."""
        # Train the model
        self.engine.train_content_based_model(self.pet_data)
        
        # Check that model components are created
        self.assertIsNotNone(self.engine.content_transformer)
        self.assertIsNotNone(self.engine.pet_features)
        self.assertIsNotNone(self.engine.pet_similarity)
        
        # Check similarity matrix dimensions
        self.assertEqual(self.engine.pet_similarity.shape, (10, 10))
    
    def test_content_based_recommendations(self):
        """Test getting content-based recommendations."""
        # Train the model
        self.engine.train_content_based_model(self.pet_data)
        
        # Get recommendations for a Labrador
        recs = self.engine.get_content_based_recommendations([1], num_recommendations=3)
        
        # Should recommend other dogs, especially Labradors
        self.assertEqual(len(recs), 3)
        self.assertIn(2, recs)  # Other Labrador should be recommended
        
        # Get recommendations for a Siamese cat
        recs = self.engine.get_content_based_recommendations([4], num_recommendations=3)
        
        # Should recommend other cats, especially Siamese
        self.assertEqual(len(recs), 3)
        self.assertIn(5, recs)  # Other Siamese should be recommended
    
    def test_multiple_pet_recommendations(self):
        """Test recommendations based on multiple pets."""
        # Train the model
        self.engine.train_content_based_model(self.pet_data)
        
        # Get recommendations for a Labrador and a Siamese cat
        recs = self.engine.get_content_based_recommendations([1, 4], num_recommendations=6)
        
        # Should include both dogs and cats
        self.assertEqual(len(recs), 6)
        
        # Count species in recommendations
        species_counts = {}
        for pet_id in recs:
            species = self.pet_data.loc[self.pet_data['id'] == pet_id, 'species'].iloc[0]
            species_counts[species] = species_counts.get(species, 0) + 1
        
        # Both dogs and cats should be represented
        self.assertIn('Dog', species_counts)
        self.assertIn('Cat', species_counts)


class CollaborativeRecommendationTests(unittest.TestCase):
    """Test collaborative filtering recommendations."""
    
    def setUp(self):
        """Set up test data."""
        # Create a temporary directory for model files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create the recommendation engine
        self.engine = HybridRecommendationEngine(model_dir=self.temp_dir)
        
        # Create sample pet data
        self.pet_data = pd.DataFrame({
            'id': range(1, 11),
            'species': ['Dog', 'Dog', 'Dog', 'Cat', 'Cat', 'Cat', 'Small Animal', 'Small Animal', 'Bird', 'Reptile'],
        })
        
        # Create sample interaction data
        # User 1 likes dogs and birds
        # User 2 likes cats and reptiles
        # User 3 likes dogs and small animals
        interactions = []
        
        # User 1 interactions
        for pet_id in [1, 2, 3, 9]:  # Dogs and bird
            interactions.append({
                'user_id': 1,
                'pet_id': pet_id,
                'interaction_type': 'view',
                'timestamp': timezone.now(),
                'duration': 60
            })
        
        # User 2 interactions
        for pet_id in [4, 5, 6, 10]:  # Cats and reptile
            interactions.append({
                'user_id': 2,
                'pet_id': pet_id,
                'interaction_type': 'view',
                'timestamp': timezone.now(),
                'duration': 60
            })
        
        # User 3 interactions
        for pet_id in [1, 3, 7, 8]:  # Dogs and small animals
            interactions.append({
                'user_id': 3,
                'pet_id': pet_id,
                'interaction_type': 'view',
                'timestamp': timezone.now(),
                'duration': 60
            })
        
        # Additional shared interests to establish similarity
        # Both User 1 and User 3 like Pet 1 and 3
        # Both User 2 and User 4 like Pet 5
        
        # User 4 interactions (similar to User 2)
        for pet_id in [5, 6]:  # Some cats
            interactions.append({
                'user_id': 4,
                'pet_id': pet_id,
                'interaction_type': 'view',
                'timestamp': timezone.now(),
                'duration': 60
            })
        
        # User 5 interactions (similar to User 1)
        for pet_id in [1, 9]:  # Some dogs and bird
            interactions.append({
                'user_id': 5,
                'pet_id': pet_id,
                'interaction_type': 'view',
                'timestamp': timezone.now(),
                'duration': 60
            })
        
        self.interaction_data = pd.DataFrame(interactions)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory and all files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_collaborative_model_training(self):
        """Test that the collaborative model can be trained."""
        # Train the model
        self.engine.train_collaborative_model(self.interaction_data)
        
        # Check that model components are created
        self.assertIsNotNone(self.engine.interaction_matrix)
        self.assertIsNotNone(self.engine.user_similarity)
        
        # Check matrix dimensions
        self.assertEqual(self.engine.interaction_matrix.shape, (5, 10))  # 5 users, 10 pets
        self.assertEqual(self.engine.user_similarity.shape, (5, 5))  # 5 users
    
    def test_collaborative_recommendations(self):
        """Test getting collaborative recommendations."""
        # Train the model
        self.engine.train_collaborative_model(self.interaction_data)
        
        # Get recommendations for User 4 (similar to User 2)
        recs = self.engine.get_collaborative_recommendations(4, num_recommendations=3)
        
        # Should recommend pets that User 2 liked but User 4 hasn't seen
        self.assertGreater(len(recs), 0)
        
        # User 4 has only seen Pet 5 and 6, so should recommend Pet 4 (cat) and Pet 10 (reptile)
        for pet_id in recs:
            self.assertNotIn(pet_id, [5, 6])  # Shouldn't recommend pets the user has already seen
        
        # Check if Pet 4 or Pet 10 is in recommendations
        pet_ids_in_recs = set(recs)
        self.assertTrue(len(pet_ids_in_recs.intersection({4, 10})) > 0)
    
    def test_cold_start_collaborative(self):
        """Test collaborative recommendations for a new user with no history."""
        # Train the model
        self.engine.train_collaborative_model(self.interaction_data)
        
        # Get recommendations for a new user
        recs = self.engine.get_collaborative_recommendations(6, num_recommendations=3)
        
        # Should return an empty list for a user with no history
        self.assertEqual(len(recs), 0)


class HybridRecommendationTests(unittest.TestCase):
    """Test hybrid recommendation system."""
    
    def setUp(self):
        """Set up test data."""
        # Create a temporary directory for model files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create the recommendation engine
        self.engine = HybridRecommendationEngine(model_dir=self.temp_dir)
        
        # Create sample pet data
        self.pet_data = pd.DataFrame({
            'id': range(1, 11),
            'name': [f'Pet{i}' for i in range(1, 11)],
            'species': ['Dog', 'Dog', 'Dog', 'Cat', 'Cat', 'Cat', 'Small Animal', 'Small Animal', 'Bird', 'Reptile'],
            'breed': ['Labrador', 'Labrador', 'Poodle', 'Siamese', 'Siamese', 'Persian', 'Hamster', 'Guinea Pig', 'Canary', 'Gecko'],
            'age': [2, 3, 5, 1, 2, 4, 1, 2, 1, 3],
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
            'size': ['Large', 'Large', 'Medium', 'Small', 'Small', 'Medium', 'Small', 'Small', 'Small', 'Small'],
            'energy_level': ['High', 'High', 'Medium', 'Low', 'Medium', 'Low', 'High', 'Medium', 'Medium', 'Low'],
            'health_status': ['Healthy'] * 10,
            'behavior_traits': ['Friendly'] * 10,
            'description': ['A pet description.'] * 10
        })
        
        # Create sample interaction data
        interactions = []
        
        # User 1 interactions (likes dogs)
        for pet_id in [1, 2, 3]:
            interactions.append({
                'user_id': 1,
                'pet_id': pet_id,
                'interaction_type': 'view',
                'timestamp': timezone.now(),
                'duration': 60
            })
        
        # User 2 interactions (likes cats)
        for pet_id in [4, 5, 6]:
            interactions.append({
                'user_id': 2,
                'pet_id': pet_id,
                'interaction_type': 'view',
                'timestamp': timezone.now(),
                'duration': 60
            })
        
        self.interaction_data = pd.DataFrame(interactions)
        
        # Train both models
        self.engine.train_content_based_model(self.pet_data)
        self.engine.train_collaborative_model(self.interaction_data)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory and all files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_hybrid_recommendations(self):
        """Test getting hybrid recommendations."""
        # Mock the _get_user_history and _get_user_adopted_pets methods
        with mock.patch.object(self.engine, '_get_user_history', return_value=[1, 2, 3]):
            with mock.patch.object(self.engine, '_get_user_adopted_pets', return_value=[]):
                # Get recommendations for User 1 (who likes dogs)
                recs = self.engine.get_hybrid_recommendations(1, num_recommendations=5)
                
                # Should return recommendations with scores
                self.assertGreater(len(recs), 0)
                self.assertEqual(len(recs[0]), 2)  # (pet_id, score)
                
                # Check that returned scores are normalized between 0 and 1
                for pet_id, score in recs:
                    self.assertGreaterEqual(score, 0)
                    self.assertLessEqual(score, 1)
    
    def test_personalized_recommendations(self):
        """Test getting personalized recommendations with preferences."""
        # Mock internal methods to return specific values
        with mock.patch.object(self.engine, '_get_user_history', return_value=[1, 2, 3]):
            with mock.patch.object(self.engine, '_get_user_adopted_pets', return_value=[]):
                with mock.patch.object(self.engine, '_get_recent_views', return_value=[1, 2]):
                    with mock.patch.object(self.engine, '_get_user_preferences', return_value={
                        'preferred_species': 'Dog',
                        'preferred_age_min': 1,
                        'preferred_age_max': 5
                    }):
                        with mock.patch.object(self.engine, '_get_pet_details', return_value={
                            'id': 1,
                            'species': 'Dog',
                            'breed': 'Labrador',
                            'age': 2,
                            'gender': 'Male',
                            'size': 'Large',
                            'energy_level': 'High'
                        }):
                            # Get personalized recommendations
                            recs = self.engine.get_recommendations_for_user(1, num_recommendations=3)
                            
                            # Should return recommendations with scores and reasons
                            self.assertGreater(len(recs), 0)
                            self.assertIn('pet_id', recs[0])
                            self.assertIn('score', recs[0])
                            self.assertIn('reason', recs[0])


class DjangoModelTests(TestCase):
    """Test Django models related to recommendations."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test shelter
        self.shelter = Shelter.objects.create(
            name='Test Shelter',
            address='123 Test St',
            phone='1234567890',
            email='test@example.com'
        )
        
        # Create test pets
        self.pet1 = Pet.objects.create(
            name='Buddy',
            species='Dog',
            breed='Labrador',
            age=2,
            gender='Male',
            size='Large',
            energy_level='High',
            health_status='Healthy',
            behavior_traits='Friendly, Playful',
            description='A friendly Labrador who loves to play fetch.',
            location='Test Location',
            shelter=self.shelter,
            available=True,
            arrival_date=timezone.now().date()
        )
        
        self.pet2 = Pet.objects.create(
            name='Whiskers',
            species='Cat',
            breed='Siamese',
            age=3,
            gender='Female',
            size='Small',
            energy_level='Medium',
            health_status='Healthy',
            behavior_traits='Independent, Calm',
            description='A calm Siamese cat who likes to be independent.',
            location='Test Location',
            shelter=self.shelter,
            available=True,
            arrival_date=timezone.now().date()
        )
        
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # Create user preferences
        self.preferences = UserPreference.objects.create(
            user=self.user,
            preferred_species='Dog',
            preferred_age_min=1,
            preferred_age_max=5,
            preferred_size='Large',
            preferred_energy_level='High'
        )
    
    def test_user_preference_to_dict(self):
        """Test the to_dict method of UserPreference."""
        prefs_dict = self.preferences.to_dict()
        
        self.assertEqual(prefs_dict['preferred_species'], 'Dog')
        self.assertEqual(prefs_dict['preferred_age_min'], 1)
        self.assertEqual(prefs_dict['preferred_age_max'], 5)
        self.assertEqual(prefs_dict['preferred_size'], 'Large')
        self.assertEqual(prefs_dict['preferred_energy_level'], 'High')
    
    def test_user_view_history(self):
        """Test creating and retrieving user view history."""
        # Create a view record
        view = UserViewHistory.objects.create(
            user=self.user,
            pet=self.pet1,
            view_duration=60,
            species=self.pet1.species
        )
        
        # Check values
        self.assertEqual(view.user, self.user)
        self.assertEqual(view.pet, self.pet1)
        self.assertEqual(view.species, 'Dog')
        
        # Test retrieval
        user_views = UserViewHistory.objects.filter(user=self.user)
        self.assertEqual(user_views.count(), 1)
        self.assertEqual(user_views[0].pet, self.pet1)
    
    def test_pet_recommendation(self):
        """Test creating and retrieving pet recommendations."""
        # Create a recommendation
        rec = PetRecommendation.objects.create(
            user=self.user,
            pet=self.pet1,
            score=0.95,
            reason='Based on your preferences'
        )
        
        # Check values
        self.assertEqual(rec.user, self.user)
        self.assertEqual(rec.pet, self.pet1)
        self.assertEqual(rec.score, 0.95)
        self.assertEqual(rec.reason, 'Based on your preferences')
        self.assertFalse(rec.viewed)
        
        # Test retrieval
        user_recs = PetRecommendation.objects.filter(user=self.user)
        self.assertEqual(user_recs.count(), 1)
        self.assertEqual(user_recs[0].pet, self.pet1)


class RecommendationViewsTests(TestCase):
    """Test views related to recommendations."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test shelter
        self.shelter = Shelter.objects.create(
            name='Test Shelter',
            address='123 Test St',
            phone='1234567890',
            email='test@example.com'
        )
        
        # Create test pets
        self.pet1 = Pet.objects.create(
            name='Buddy',
            species='Dog',
            breed='Labrador',
            age=2,
            gender='Male',
            size='Large',
            energy_level='High',
            health_status='Healthy',
            behavior_traits='Friendly, Playful',
            description='A friendly Labrador who loves to play fetch.',
            location='Test Location',
            shelter=self.shelter,
            available=True,
            arrival_date=timezone.now().date()
        )
        
        self.pet2 = Pet.objects.create(
            name='Whiskers',
            species='Cat',
            breed='Siamese',
            age=3,
            gender='Female',
            size='Small',
            energy_level='Medium',
            health_status='Healthy',
            behavior_traits='Independent, Calm',
            description='A calm Siamese cat who likes to be independent.',
            location='Test Location',
            shelter=self.shelter,
            available=True,
            arrival_date=timezone.now().date()
        )
        
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # Create user preferences
        self.preferences = UserPreference.objects.create(
            user=self.user,
            preferred_species='Dog',
            preferred_age_min=1,
            preferred_age_max=5,
            preferred_size='Large',
            preferred_energy_level='High'
        )
        
        # Create a recommendation
        self.recommendation = PetRecommendation.objects.create(
            user=self.user,
            pet=self.pet1,
            score=0.95,
            reason='Based on your preferences'
        )
        
        # Login the user
        self.client.login(username='testuser', password='testpass')
    
    def test_get_user_recommendations(self):
        """Test the get_user_recommendations helper function."""
        with mock.patch('pets.views.generate_recommendations') as mock_generate:
            # Mock the generate_recommendations function to return a list of recommendations
            mock_recommendations = [self.recommendation]
            mock_generate.return_value = mock_recommendations
            
            # Call the get_user_recommendations function
            recommendations = get_user_recommendations(self.user.id)
            
            # Check that it returns the mocked recommendations
            self.assertEqual(recommendations, mock_recommendations)
            
            # Verify that generate_recommendations was not called (since we have recent recommendations)
            mock_generate.assert_not_called()
            
            # Delete the recommendation and create an old one (older than 24 hours)
            self.recommendation.delete()
            old_date = timezone.now() - timedelta(hours=25)
            old_recommendation = PetRecommendation.objects.create(
                user=self.user,
                pet=self.pet1,
                score=0.95,
                reason='Based on your preferences',
                created_at=old_date
            )
            
            # Call the get_user_recommendations function again
            recommendations = get_user_recommendations(self.user.id)
            
            # This time generate_recommendations should be called
            mock_generate.assert_called_once_with(self.user.id, 10)
    
    def test_log_pet_view(self):
        """Test the log_pet_view helper function."""
        # Count initial views
        initial_count = UserViewHistory.objects.filter(user=self.user, pet=self.pet1).count()
        
        # Log a view
        log_pet_view(self.user.id, self.pet1.id, 60)
        
        # Count views after logging
        after_count = UserViewHistory.objects.filter(user=self.user, pet=self.pet1).count()
        
        # Should have created a new view record
        self.assertEqual(after_count, initial_count + 1)
        
        # Check the view record
        view = UserViewHistory.objects.filter(user=self.user, pet=self.pet1).latest('timestamp')
        self.assertEqual(view.view_duration, 60)
        self.assertEqual(view.species, self.pet1.species)
        
        # Create a recommendation for the pet
        recommendation = PetRecommendation.objects.create(
            user=self.user,
            pet=self.pet1,
            score=0.95,
            reason='Based on your preferences',
            viewed=False
        )
        
        # Log another view
        log_pet_view(self.user.id, self.pet1.id, 30)
        
        # Check that the recommendation was marked as viewed
        recommendation.refresh_from_db()
        self.assertTrue(recommendation.viewed)


class RecommendationSystemIntegrationTest(TestCase):
    """Integration test for the recommendation system."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test shelter
        self.shelter = Shelter.objects.create(
            name='Test Shelter',
            address='123 Test St',
            phone='1234567890',
            email='test@example.com'
        )
        
        # Create test pets (6 dogs, 4 cats)
        self.dogs = []
        self.cats = []
        
        for i in range(6):
            dog = Pet.objects.create(
                name=f'Dog{i+1}',
                species='Dog',
                breed='Mix',
                age=i+1,
                gender='Male' if i % 2 == 0 else 'Female',
                size='Medium',
                energy_level='Medium',
                health_status='Healthy',
                behavior_traits='Friendly',
                description='A friendly dog.',
                location='Test Location',
                shelter=self.shelter,
                available=True,
                arrival_date=timezone.now().date()
            )
            self.dogs.append(dog)
        
        for i in range(4):
            cat = Pet.objects.create(
                name=f'Cat{i+1}',
                species='Cat',
                breed='Mix',
                age=i+1,
                gender='Male' if i % 2 == 0 else 'Female',
                size='Small',
                energy_level='Low',
                health_status='Healthy',
                behavior_traits='Independent',
                description='A calm cat.',
                location='Test Location',
                shelter=self.shelter,
                available=True,
                arrival_date=timezone.now().date()
            )
            self.cats.append(cat)
        
        # Create test users
        self.dog_lover = User.objects.create_user(
            username='doglover',
            email='dog@example.com',
            password='testpass'
        )
        
        self.cat_lover = User.objects.create_user(
            username='catlover',
            email='cat@example.com',
            password='testpass'
        )
        
        self.undecided = User.objects.create_user(
            username='undecided',
            email='undecided@example.com',
            password='testpass'
        )
        
        # Create user preferences
        UserPreference.objects.create(
            user=self.dog_lover,
            preferred_species='Dog',
            preferred_age_min=1,
            preferred_age_max=5,
            preferred_size='Medium',
            preferred_energy_level='Medium'
        )
        
        UserPreference.objects.create(
            user=self.cat_lover,
            preferred_species='Cat',
            preferred_age_min=1,
            preferred_age_max=5,
            preferred_size='Small',
            preferred_energy_level='Low'
        )
        
        # No preferences for undecided user
        
        # Create view history for users
        # Dog lover views mostly dogs
        for i in range(4):
            UserViewHistory.objects.create(
                user=self.dog_lover,
                pet=self.dogs[i],
                species='Dog',
                view_duration=60
            )
        
        # But also one cat
        UserViewHistory.objects.create(
            user=self.dog_lover,
            pet=self.cats[0],
            species='Cat',
            view_duration=30
        )
        
        # Cat lover views only cats
        for i in range(3):
            UserViewHistory.objects.create(
                user=self.cat_lover,
                pet=self.cats[i],
                species='Cat',
                view_duration=60
            )
        
        # Undecided user views both
        UserViewHistory.objects.create(
            user=self.undecided,
            pet=self.dogs[0],
            species='Dog',
            view_duration=60
        )
        
        UserViewHistory.objects.create(
            user=self.undecided,
            pet=self.cats[0],
            species='Cat',
            view_duration=60
        )
    
    @mock.patch('pets.views.AdaptiveRecommendationEngine.get_recommendations')
    def test_adaptive_recommendations(self, mock_get_recommendations):
        """Test the adaptive recommendation engine."""
        # Mock the get_recommendations method to return specific pets
        dog_recs = [dog.id for dog in self.dogs[4:]]  # Dogs not yet viewed
        cat_recs = [cat.id for cat in self.cats[1:]]  # Cats not yet viewed
        
        # Set up different returns based on user_id
        def side_effect(user_id, *args, **kwargs):
            if user_id == self.dog_lover.id:
                return dog_recs  # Return dogs for dog lover
            elif user_id == self.cat_lover.id:
                return cat_recs  # Return cats for cat lover
            else:
                return dog_recs[:2] + cat_recs[:2]  # Mix for undecided user
        
        mock_get_recommendations.side_effect = side_effect
        
        # Login as dog lover and view a recommendation
        self.client.login(username='doglover', password='testpass')
        response = self.client.get('/')  # Home page with recommendations
        
        # Now log a view for a recommended dog
        log_pet_view(self.dog_lover.id, dog_recs[0], 60)
        
        # Logout and login as cat lover
        self.client.logout()
        self.client.login(username='catlover', password='testpass')
        response = self.client.get('/')  # Home page with recommendations
        
        # Now log a view for a recommended cat
        log_pet_view(self.cat_lover.id, cat_recs[0], 60)
        
        # Logout and login as undecided user
        self.client.logout()
        self.client.login(username='undecided', password='testpass')
        response = self.client.get('/')  # Home page with recommendations
        
        # Log several cat views to shift preferences
        for cat_id in cat_recs:
            log_pet_view(self.undecided.id, cat_id, 60)
        
        # Mock should have been called multiple times
        self.assertGreater(mock_get_recommendations.call_count, 3)


if __name__ == '__main__':
    unittest.main()

        