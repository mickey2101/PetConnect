# recommendations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationView, get_csrf_token, RecentViewsView, record_animal_view

# For backward compatibility, we keep the router
router = DefaultRouter()
router.register(r'', RecommendationView, basename='recommendation')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Add CSRF token endpoint
    path('csrf/', get_csrf_token, name='recommendations_csrf'),
    
    # Add recent views endpoint
    path('recent-views/', RecentViewsView.as_view(), name='recent_views'),
    
    # Add record view endpoint (for backward compatibility)
    path('record-view/', record_animal_view, name='record_view'),
]