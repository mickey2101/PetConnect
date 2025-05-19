from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def get_csrf_token(request):
    """
    View to get a CSRF token.
    This can be called by your React app on initialization to ensure a CSRF cookie is set.
    """
    return JsonResponse({'success': True})

urlpatterns = [
    path('api/csrf/', get_csrf_token, name='csrf'),
]