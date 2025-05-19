#animals/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnimalListView,LogAnimalViewView, get_csrf_token , AnimalDetailView

router = DefaultRouter()

urlpatterns = [
    path('', AnimalListView.as_view(), name='animal-list'),
    path('<int:pk>/', AnimalDetailView.as_view(), name='animal-detail'),
    # Add these new URL patterns
    path('record-view/', LogAnimalViewView.as_view(), name='record_animal_view'),
    path('csrf/', get_csrf_token, name='csrf'),
]