# animals/models.py
from django.db import models
from django.utils import timezone

class Shelter(models.Model):
    """Model representing an animal shelter"""
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Animal(models.Model):
    """Model representing an animal available for adoption"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown')
    ]
    
    STATUS_CHOICES = [
        ('A', 'Available'),
        ('P', 'Pending'),
        ('AD', 'Adopted'),
    ]
    SIZE_CHOICES = [
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
    ]
    
    ENERGY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)  # Dog, Cat, etc.
    breed = models.CharField(max_length=100, blank=True)
    age_years = models.IntegerField(default=0)
    age_months = models.IntegerField(default=0)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='animals', null=True, blank=True)
    
    # Add the new fields
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='Medium')
    energy_level = models.CharField(max_length=10, choices=ENERGY_CHOICES, default='Medium')
    

    # Health attributes
    vaccinated = models.BooleanField(default=False)
    neutered = models.BooleanField(default=False)
    health_notes = models.TextField(blank=True)
    
    # Behavioral attributes
    good_with_kids = models.BooleanField(default=True)
    good_with_cats = models.BooleanField(default=True)
    good_with_dogs = models.BooleanField(default=True)
    behavior_notes = models.TextField(blank=True)
    
    # Description and status
    description = models.TextField(blank=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='A')
    arrival_date = models.DateField(default=timezone.now)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.breed} ({self.get_status_display()})"
    
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AnimalViewHistory(models.Model):
    """Model for tracking which animals a user has viewed."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    view_duration = models.IntegerField(default=0, help_text="Duration of view in seconds")
    species = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Animal view histories"
        
    def __str__(self):
        return f"{self.user.username} viewed {self.animal.name} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        """Override save to automatically set the species from the animal."""
        if not self.species and self.animal:
            self.species = self.animal.species
        super().save(*args, **kwargs)