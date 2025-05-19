"""
Pet Connect - Update Recommendations Command
------------------------------------------
Management command to update all recommendations.

Author: Macayla van der Merwe
"""

import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recommendations.recommendation_engine import PetConnectRecommendationEngine

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates recommendations for all users or a specific user'
    
    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=int, help='User ID to update recommendations for')
        parser.add_argument('--limit', type=int, default=20, help='Number of recommendations to generate per user')
    
    def handle(self, *args, **options):
        recommendation_engine = PetConnectRecommendationEngine()
        user_id = options.get('user_id')
        limit = options.get('limit')
        
        if user_id:
            # Update for specific user
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f"Updating recommendations for user: {user.username}")
                
                recommendations = recommendation_engine.get_recommendations(user_id, limit)
                
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully updated {len(recommendations)} recommendations for user {user.username}"
                ))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found"))
        else:
            # Update for all users
            users = User.objects.all()
            total = users.count()
            
            self.stdout.write(f"Updating recommendations for {total} users")
            
            for i, user in enumerate(users):
                try:
                    recommendations = recommendation_engine.get_recommendations(user.id, limit)
                    self.stdout.write(f"[{i+1}/{total}] Updated {len(recommendations)} recommendations for user {user.username}")
                except Exception as e:
                    logger.error(f"Error updating recommendations for user {user.id}: {str(e)}")
                    self.stdout.write(self.style.ERROR(f"Error updating recommendations for user {user.username}"))
            
            self.stdout.write(self.style.SUCCESS("Successfully updated recommendations for all users"))