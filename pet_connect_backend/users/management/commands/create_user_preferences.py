# users/management/commands/create_user_preferences.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Create default preferences for all users'

    def handle(self, *args, **options):
        # Get all users
        users = User.objects.all()
        self.stdout.write(f"Found {users.count()} users")
        
        preferences_created = 0
        preferences_existed = 0
        
        for user in users:
            self.stdout.write(f"Processing user: {user.username}")
            
            try:
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'has_children': False,
                        'has_other_dogs': False,
                        'has_other_cats': False,
                        'preferred_animal_type': 'Dog',  # Default preference
                        'preferred_age_min': 0,
                        'preferred_age_max': 120,  # 10 years
                        'phone_number': '',
                        'address': '',
                    }
                )
                
                if created:
                    preferences_created += 1
                    self.stdout.write(self.style.SUCCESS(f"Created preferences for user: {user.username}"))
                else:
                    preferences_existed += 1
                    self.stdout.write(f"Preferences already exist for user: {user.username}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating preferences for {user.username}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"\nSummary: Created {preferences_created} new preferences, {preferences_existed} already existed"))