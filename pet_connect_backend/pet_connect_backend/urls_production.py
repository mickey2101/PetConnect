"""
Production URL configuration for pet_connect_backend project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from animals.views import AnimalViewSet
from recommendations.views import (
    RecommendationView, 
    record_animal_view, 
    RecentViewsView,
)

# Import the original urlpatterns
from pet_connect_backend.urls import router, get_csrf_token

# Test view to verify Django is working
def test_view(request):
    return HttpResponse("<html><body><h1>Django is running!</h1><p>If you see this message, the server is working correctly.</p></body></html>")

# Debug view to show system paths
def debug_view(request):
    import sys
    import os
    from django.conf import settings
    
    # Get project structure
    base_dir = settings.BASE_DIR
    template_dirs = settings.TEMPLATES[0]['DIRS']
    static_dirs = settings.STATICFILES_DIRS if hasattr(settings, 'STATICFILES_DIRS') else []
    
    # Check if frontend_build exists
    frontend_build_path = os.path.join(settings.BASE_DIR, 'frontend_build')
    frontend_build_exists = os.path.exists(frontend_build_path)
    
    absolute_frontend_build = '/app/frontend_build'
    absolute_exists = os.path.exists(absolute_frontend_build)
    
    # Check for index.html
    index_paths = [
        os.path.join(dir_path, 'index.html') 
        for dir_path in template_dirs
    ]
    
    index_exists = [os.path.exists(path) for path in index_paths]
    
    # List directories
    try:
        root_dir_contents = os.listdir('/app')
    except:
        root_dir_contents = ['Error listing /app']
        
    response_data = {
        'python_version': sys.version,
        'base_dir': str(base_dir),
        'template_dirs': [str(p) for p in template_dirs],
        'static_dirs': [str(p) for p in static_dirs],
        'frontend_build_path': frontend_build_path,
        'frontend_build_exists': frontend_build_exists,
        'absolute_frontend_build': absolute_frontend_build,
        'absolute_exists': absolute_exists,
        'index_paths': index_paths,
        'index_exists': index_exists,
        'root_dir_contents': root_dir_contents,
    }
    
    return JsonResponse(response_data)

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
    
    # Test endpoints
    path('test/', test_view, name='test_view'),
    path('debug/', debug_view, name='debug_view'),
]

# Add the catch-all for the React app
urlpatterns = api_urlpatterns + [
    # This will serve the React frontend for any path not matched above
    re_path(r'^(?!api/|admin/|test/|debug/).*$', TemplateView.as_view(template_name='index.html')),
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