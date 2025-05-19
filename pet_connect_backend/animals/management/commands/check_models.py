from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Check model structures for recommendation engine compatibility'

    def handle(self, *args, **options):
        self.stdout.write("Checking model structures...")
        
        # Check UserProfile structure
        try:
            UserProfile = apps.get_model('users', 'UserProfile')
            self.stdout.write("UserProfile model exists")
            
            # Get fields
            fields = [field.name for field in UserProfile._meta.get_fields()]
            self.stdout.write(f"UserProfile fields: {', '.join(fields)}")
            
            # Check for specific fields
            recommendation_fields = ['has_children', 'has_other_dogs', 'has_other_cats', 
                                    'preferred_species', 'min_age_months', 'max_age_months',
                                    'preferred_gender']
            
            missing_fields = [field for field in recommendation_fields if field not in fields]
            if missing_fields:
                self.stdout.write(self.style.WARNING(f"Missing fields in UserProfile: {', '.join(missing_fields)}"))
            else:
                self.stdout.write(self.style.SUCCESS("UserProfile has all needed fields"))
                
        except LookupError as e:
            self.stdout.write(self.style.ERROR(f"Error finding UserProfile model: {e}"))
        
        # Check Animal structure
        try:
            Animal = apps.get_model('animals', 'Animal')
            self.stdout.write("Animal model exists")
            
            # Get fields
            fields = [field.name for field in Animal._meta.get_fields()]
            self.stdout.write(f"Animal fields: {', '.join(fields)}")
            
        except LookupError as e:
            self.stdout.write(self.style.ERROR(f"Error finding Animal model: {e}"))
        
        # Check if AnimalRecommendation model exists
        try:
            AnimalRecommendation = apps.get_model('recommendations', 'AnimalRecommendation')
            self.stdout.write("AnimalRecommendation model exists")
            
            # Get fields
            fields = [field.name for field in AnimalRecommendation._meta.get_fields()]
            self.stdout.write(f"AnimalRecommendation fields: {', '.join(fields)}")
            
        except LookupError as e:
            self.stdout.write(self.style.ERROR(f"Error finding AnimalRecommendation model: {e}"))