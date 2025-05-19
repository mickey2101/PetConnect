"""
Pet Connect - Animal Views
-------------------------
Views for handling animal data, filtering, and logging animal views for the recommendation system.

Author: Macayla van der Merwe
"""

import logging
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import Animal, AnimalViewHistory
from .serializers import AnimalSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

# Set up logging
logger = logging.getLogger(__name__)


class AnimalDetailView(RetrieveAPIView):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer

class AnimalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing animals.
    """
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @method_decorator(ensure_csrf_cookie)
    def retrieve(self, request, *args, **kwargs):
        """
        Get a specific animal by ID.
        Also logs the view if the user is authenticated.
        """
        response = super().retrieve(request, *args, **kwargs)
        
        # Log the view if user is authenticated
        if request.user.is_authenticated:
            try:
                animal = self.get_object()
                
                # Log the view
                AnimalViewHistory.objects.create(
                    user=request.user,
                    animal=animal,
                    species=animal.species
                )
                
                logger.debug(f"User {request.user.id} viewed animal {animal.id}")
            except Exception as e:
                logger.error(f"Error logging animal view: {str(e)}")
        
        return response


class AnimalListView(APIView):
    """
    API view for filtering animals by various criteria.
    """
    permission_classes = [AllowAny]
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """Get filtered animals"""
        animals = Animal.objects.all()

        # Apply filters from query parameters
        species = request.query_params.get('species')
        size = request.query_params.get('size')
        energy_level = request.query_params.get('energy_level')
        gender = request.query_params.get('gender')
        age_min = request.query_params.get('age_min')
        age_max = request.query_params.get('age_max')

        # Apply filters if specified
        if species:
            animals = animals.filter(species__iexact=species)
        if size:
            animals = animals.filter(size__iexact=size)
        if energy_level:
            animals = animals.filter(energy_level__iexact=energy_level)
        if gender:
            animals = animals.filter(gender__iexact=gender)
        if age_min:
            # Handle both age_months and age fields
            if hasattr(Animal, 'age_months'):
                animals = animals.filter(age_months__gte=int(age_min))
            else:
                animals = animals.filter(age__gte=float(age_min) / 12)
        if age_max:
            # Handle both age_months and age fields
            if hasattr(Animal, 'age_months'):
                animals = animals.filter(age_months__lte=int(age_max))
            else:
                animals = animals.filter(age__lte=float(age_max) / 12)

        serializer = AnimalSerializer(animals, many=True)
        return Response(serializer.data)


class LogAnimalViewView(APIView):
        """API view to log animal views for recommendation tracking"""
        
        @method_decorator(ensure_csrf_cookie)
        def post(self, request):
            animal_id = request.data.get('animal_id')
            view_duration = request.data.get('view_duration', 0)
            
            if not animal_id:
                return Response({'error': 'Animal ID is required'}, status=status.HTTP_400_BAD_REQUEST)
                
            if not request.user.is_authenticated:
                return Response({'error': 'Authentication required'}, status=status.HTTP_403_FORBIDDEN)
                
            try:
                animal = Animal.objects.get(id=animal_id)
                
                # Create view history entry
                view = AnimalViewHistory.objects.create(
                    user=request.user,
                    animal=animal,
                    view_duration=view_duration,
                    species=animal.species
                )
                
                return Response({'success': True, 'view_id': view.id})
                
            except Animal.DoesNotExist:
                return Response({'error': 'Animal not found'}, status=status.HTTP_404_NOT_FOUND)

@ensure_csrf_cookie
def get_csrf_token(request):
    """
    View to get a CSRF token.
    This can be called by your React app on initialization to ensure a CSRF cookie is set.
    """
    return JsonResponse({'success': True})