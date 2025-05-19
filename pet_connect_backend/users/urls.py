from django.urls import path
from .views import (
    CurrentUserView,
    LoginView,
    LogoutView,
    RegisterView,
    UserPreferenceView,
    UpdateProfileView,  # Add this import
    get_csrf_token,
    )

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('preferences/', UserPreferenceView.as_view(), name='user_preferences'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),  # Add this URL
    path('csrf/', get_csrf_token, name='csrf_token'),
]
