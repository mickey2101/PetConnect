"""
Pet Connect - Recommendations Serializers
----------------------------------------
Serializers for recommendation models.

Author: Macayla van der Merwe
"""

from rest_framework import serializers
from animals.serializers import AnimalSerializer
from .models import AnimalRecommendation

class AnimalRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for the AnimalRecommendation model"""
    animal = AnimalSerializer(read_only=True)
    
    class Meta:
        model = AnimalRecommendation
        fields = ['id', 'user', 'animal', 'score', 'preference_score', 'interaction_score', 
                  'similarity_score', 'reason', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class RecommendationListSerializer(serializers.Serializer):
    """Serializer for recommendation list responses"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    species = serializers.CharField()
    breed = serializers.CharField(required=False, allow_blank=True)
    age = serializers.FloatField(required=False)
    image_url = serializers.URLField(required=False, allow_null=True)
    score = serializers.FloatField()
    reason = serializers.CharField(required=False, allow_blank=True)