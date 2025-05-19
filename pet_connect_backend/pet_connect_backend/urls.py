# pet_connect_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter  # Add this line
from animals.views import AnimalViewSet
from recommendations.views import (
    RecommendationView, 
    record_animal_view, 
    RecentViewsView,
    get_csrf_token
)

router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')

# CSRF token view
@ensure_csrf_cookie
def get_csrf_token(request):
    """View to get a CSRF token."""
    return JsonResponse({'success': True})

urlpatterns = [
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

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
handler403 = 'django.views.defaults.permission_denied'
handler400 = 'django.views.defaults.bad_request'