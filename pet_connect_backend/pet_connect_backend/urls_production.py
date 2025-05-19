"""
Production URL configuration for pet_connect_backend project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from animals.views import AnimalViewSet
from recommendations.views import (
    RecommendationView, 
    record_animal_view, 
    RecentViewsView,
)

# Import the original urlpatterns
from .urls import router, get_csrf_token

# Define all your API endpoints first
api_urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/csrf/', get_csrf_token, name='csrf'),
    path('api/animals/', include('animals.urls')),
    path('api/', include(router.urls)),
    path('api/users/', include('users.urls')),
    path('', include('pet_connect_backend.csrf_urls')),
    path('api/recommendations/csrf-token/', get_csrf_token, name='csrf_token'),
    path('api/recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('api/recommendations/record-view/', record_animal_view, name='record_animal_view'),
    path('api/recommendations/recent-views/', RecentViewsView.as_view(), name='recent_views'),
]

# Add the catch-all for the React app
urlpatterns = api_urlpatterns + [
    # This will serve the React frontend for any path not matched above
    re_path(r'^(?!api/|admin/).*$', TemplateView.as_view(template_name='index.html')),
]

# Serve static and media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
handler403 = 'django.views.defaults.permission_denied'
handler400 = 'django.views.defaults.bad_request'