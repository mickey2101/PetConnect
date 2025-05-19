import logging
import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from animals.models import Animal, AnimalViewHistory
from recommendations.recommendation_engine import HybridRecommendationEngine

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Train the recommendation engine with existing data'

    def handle(self, *args, **options):
        self.stdout.write('Starting recommendation model training...')
        
        try:
            # Initialize the recommendation engine
            engine = HybridRecommendationEngine()
            
            # Get animal data
            animals = Animal.objects.all()
            self.stdout.write(f'Found {animals.count()} animals in database')
            
            # Convert to dataframe
            animal_data = []
            for animal in animals:
                animal_data.append({
                    'id': animal.id,
                    'name': animal.name,
                    'species': animal.species,
                    'breed': animal.breed,
                    'age': animal.age_years,
                    'gender': animal.gender,
                    'size': animal.size,
                    'energy_level': animal.energy_level,
                    'behavior_traits': animal.behavior_traits,
                    'description': animal.description,
                })
            
            animals_df = pd.DataFrame(animal_data)
            self.stdout.write(f'Converted {len(animals_df)} animals to DataFrame')
            
            # Get interaction data
            views = AnimalViewHistory.objects.all()
            self.stdout.write(f'Found {views.count()} view records in database')
            
            # Convert to dataframe
            interaction_data = []
            for view in views:
                interaction_data.append({
                    'user_id': view.user.id,
                    'pet_id': view.animal.id,
                    'interaction_type': 'view',
                    'timestamp': view.timestamp,
                })
            
            interactions_df = pd.DataFrame(interaction_data)
            self.stdout.write(f'Converted {len(interactions_df)} interactions to DataFrame')
            
            # Train the content-based model
            if not animals_df.empty:
                self.stdout.write('Training content-based model...')
                engine.train_content_based_model(animals_df)
                self.stdout.write(self.style.SUCCESS('Content-based model trained successfully!'))
            
            # Train the collaborative model if we have enough data
            if not interactions_df.empty and len(interactions_df) >= 10:
                self.stdout.write('Training collaborative model...')
                engine.train_collaborative_model(interactions_df)
                self.stdout.write(self.style.SUCCESS('Collaborative model trained successfully!'))
            else:
                self.stdout.write(self.style.WARNING(
                    f'Not enough interaction data to train collaborative model ({len(interactions_df)} < 10)'
                ))
            
            self.stdout.write(self.style.SUCCESS('Recommendation model training completed!'))
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error training recommendation model: {str(e)}'))
            logger.error(f'Error training recommendation model: {str(e)}', exc_info=True)