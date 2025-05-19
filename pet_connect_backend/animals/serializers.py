# animals/serializers.py
from rest_framework import serializers
from .models import Animal, Shelter, AnimalViewHistory

class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = ['id', 'name', 'address', 'city', 'postal_code', 'phone', 'email', 'website']

class AnimalSerializer(serializers.ModelSerializer):
    shelter = ShelterSerializer(read_only=True)
    
    # Remove fields that don't exist in the model
    # size_display and energy_level_display don't exist because your model doesn't have those fields
    
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Calculate age properly
    age = serializers.SerializerMethodField()
    
    def get_age(self, obj):
        """Calculate age in years and months as a string"""
        if obj.age_years == 0:
            if obj.age_months == 1:
                return "1 month"
            return f"{obj.age_months} months"
        elif obj.age_years == 1:
            if obj.age_months == 0:
                return "1 year"
            elif obj.age_months == 1:
                return "1 year, 1 month"
            return f"1 year, {obj.age_months} months"
        else:
            if obj.age_months == 0:
                return f"{obj.age_years} years"
            elif obj.age_months == 1:
                return f"{obj.age_years} years, 1 month"
            return f"{obj.age_years} years, {obj.age_months} months"
    
    class Meta:
        model = Animal
        fields = [
            'id', 'name', 'species', 'breed', 'age_years', 'age_months', 'age',
            'gender', 'gender_display', 'shelter', 'vaccinated', 'neutered', 'health_notes',
            'good_with_kids', 'good_with_cats', 'good_with_dogs', 'behavior_notes',
            'description', 'status', 'status_display', 'arrival_date', 'created_at', 'updated_at'
        ]

class AnimalViewHistorySerializer(serializers.ModelSerializer):
    animal = AnimalSerializer(read_only=True)
    
    class Meta:
        model = AnimalViewHistory
        fields = ['id', 'user', 'animal', 'timestamp', 'view_duration', 'species']
        read_only_fields = ['id', 'timestamp']