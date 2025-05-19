# recommendations/views.py - Complete file

from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt  # Add this import
import logging
import traceback
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from animals.models import Animal, AnimalViewHistory
from django.contrib.auth.models import User
from django.utils import timezone
from .recommendation_engine import MLRecommendationEngine

logger = logging.getLogger(__name__)

# CSRF token view
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

class RecommendationView(APIView):
    """API view for fetching ML-enhanced recommendations"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get the current user
            user = request.user
            
            # Log request information
            logger.info(f"Serving ML recommendations for user {user.username} (id: {user.id})")
            
            # Get the recommendation engine
            engine = MLRecommendationEngine()
            
            # Get personalized recommendations
            recommended_ids = engine.get_recommendations(user.id, limit=10)
            
            # Get the full animal objects
            recommended_animals = []
            for animal_id in recommended_ids:
                try:
                    animal = Animal.objects.get(id=animal_id)
                    
                    # Get the reason for this recommendation
                    reason = engine.get_recommendation_reason(user.id, animal)
                    
                    # Create a dictionary of animal info
                    animal_data = {
                        'id': animal.id,
                        'name': animal.name,
                        'species': animal.species,
                        'breed': animal.breed,
                        'age_years': animal.age_years,
                        'age_months': animal.age_months,
                        'gender': animal.gender,
                        'size': animal.size if hasattr(animal, 'size') else None,
                        'photo_url': animal.photo_url if hasattr(animal, 'photo_url') else None,
                        'recommendation_reason': reason
                    }
                    
                    # Add compatibility fields if they exist
                    for field in ['good_with_kids', 'good_with_cats', 'good_with_dogs', 'energy_level']:
                        if hasattr(animal, field):
                            animal_data[field] = getattr(animal, field)
                    
                    recommended_animals.append(animal_data)
                    
                except Animal.DoesNotExist:
                    logger.warning(f"Recommended animal ID {animal_id} not found in database")
                    continue
                except Exception as e:
                    logger.error(f"Error processing animal ID {animal_id}: {str(e)}")
                    continue
            
            logger.info(f"Returning {len(recommended_animals)} recommendations to frontend")
            
            # Return the recommendations as JSON
            return Response({'recommendations': recommended_animals})
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# IMPORTANT: The csrf_exempt decorator MUST be the first decorator
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def record_animal_view(request):
    """API endpoint to record when a user views an animal"""
    try:
        # Print detailed request info for debugging
        logger.info(f"Recording view with data: {request.data}")
        print(f"Recording view with data: {request.data}")
        print(f"Authentication: {request.user.is_authenticated}, User: {request.user.username}")
        print(f"Headers: {request.headers}")
        
        # Get data from request
        animal_id = request.data.get('animal_id')
        
        if not animal_id:
            return Response({'error': 'Animal ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the animal
        try:
            animal = Animal.objects.get(id=animal_id)
            logger.info(f"Found animal: {animal.name} (ID: {animal.id})")
            print(f"Found animal: {animal.name} (ID: {animal.id})")
        except Animal.DoesNotExist:
            return Response({'error': 'Animal not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the user
        user = request.user
        logger.info(f"User: {user.username} (ID: {user.id})")
        print(f"User: {user.username} (ID: {user.id})")
        
        # Try creating the view record
        try:
            # Create a new view record
            view = AnimalViewHistory.objects.create(
                user=user,
                animal=animal,
                timestamp=timezone.now()
            )
            logger.info(f"Successfully created view record ID: {view.id}")
            print(f"Successfully created view record ID: {view.id}")
            
            # Count total views for this user
            count = AnimalViewHistory.objects.filter(user=user).count()
            logger.info(f"User now has {count} total view records")
            print(f"User now has {count} total view records")
            
        except Exception as e:
            logger.error(f"Error creating view record: {str(e)}")
            print(f"Error creating view record: {str(e)}")
            logger.error(traceback.format_exc())
            print(traceback.format_exc())
            
            # Try direct database access as a fallback
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    # Insert the view record directly
                    cursor.execute(
                        "INSERT INTO animals_animalviewhistory (user_id, animal_id, timestamp) VALUES (%s, %s, NOW())",
                        [user.id, animal.id]
                    )
                    logger.info(f"Direct SQL insertion for view record successful")
                    print(f"Direct SQL insertion for view record successful")
            except Exception as sql_error:
                logger.error(f"Direct SQL error: {str(sql_error)}")
                print(f"Direct SQL error: {str(sql_error)}")
                return Response({'error': f'Failed to create view record: {str(sql_error)}'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'success': True})
            
    except Exception as e:
        logger.error(f"Error recording animal view: {str(e)}")
        print(f"Error recording animal view: {str(e)}")
        logger.error(traceback.format_exc())
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecentViewsView(APIView):
    """API endpoint for fetching a user's recently viewed animals"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get the current user
            user = request.user
            logger.info(f"Fetching recent views for user: {user.username} (ID: {user.id})")
            print(f"Fetching recent views for user: {user.username} (ID: {user.id})")
            
            # Count total views for debugging
            total_views = AnimalViewHistory.objects.filter(user=user).count()
            logger.info(f"User has {total_views} total views in database")
            print(f"User has {total_views} total views in database")
            
            # Get recent views (last 5)
            recent_views = AnimalViewHistory.objects.filter(
                user=user
            ).select_related('animal').order_by('-timestamp')[:5]
            
            logger.info(f"Found {recent_views.count()} recent views")
            print(f"Found {recent_views.count()} recent views")
            
            # Print each view for debugging
            for view in recent_views:
                logger.info(f"View ID {view.id}: {view.user.username} viewed {view.animal.name} at {view.timestamp}")
                print(f"View ID {view.id}: {view.user.username} viewed {view.animal.name} at {view.timestamp}")
            
            # Convert to a list of dictionaries
            recent_views_data = []
            for view in recent_views:
                animal = view.animal
                
                # Create a dictionary of animal info
                animal_data = {
                    'id': animal.id,
                    'name': animal.name,
                    'species': animal.species,
                    'breed': animal.breed,
                    'photo_url': animal.photo_url if hasattr(animal, 'photo_url') else None,
                    'viewed_at': view.timestamp.isoformat()
                }
                
                recent_views_data.append(animal_data)
            
            logger.info(f"Returning {len(recent_views_data)} recent views to frontend")
            print(f"Returning {len(recent_views_data)} recent views to frontend")
            
            # Return the recent views as JSON
            return Response({'recent_views': recent_views_data})
            
        except Exception as e:
            logger.error(f"Error fetching recent views: {str(e)}")
            print(f"Error fetching recent views: {str(e)}")
            logger.error(traceback.format_exc())
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)