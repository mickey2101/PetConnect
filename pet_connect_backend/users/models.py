from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """User profile model to extend the standard User model"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Animal preferences
    preferred_species = models.CharField(max_length=20, blank=True, null=True)
    preferred_age_min = models.FloatField(default=0)
    preferred_age_max = models.FloatField(default=20)
    preferred_size = models.CharField(max_length=10, blank=True, null=True)
    preferred_energy_level = models.CharField(max_length=10, blank=True, null=True)
    good_with_children = models.BooleanField(default=False)
    good_with_other_pets = models.BooleanField(default=False)
    
    # Additional profile fields
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"


# Signal to create or update user profile when user is created or updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update the user profile when a user is created or updated."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Make sure the profile exists, even if the signal didn't fire when the user was created
        UserProfile.objects.get_or_create(user=instance)