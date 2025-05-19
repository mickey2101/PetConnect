# test_imports.py
# Place this in your project directory

print("Testing imports...")

# Try importing from each app
try:
    print("Importing from animals app...")
    from animals.models import Animal
    from animals.views import AnimalViewSet
    from animals.urls import urlpatterns as animals_urlpatterns
    print("Animals imports successful")
except Exception as e:
    print(f"Error importing from animals app: {e}")

try:
    print("Importing from users app...")
    from users.models import UserProfile
    from users.urls import urlpatterns as users_urlpatterns
    print("Users imports successful")
except Exception as e:
    print(f"Error importing from users app: {e}")

try:
    print("Importing from recommendations app...")
    from recommendations.models import AnimalRecommendation
    from recommendations.views import RecommendationViewSet
    from recommendations.urls import urlpatterns as recommendations_urlpatterns
    print("Recommendations imports successful")
except Exception as e:
    print(f"Error importing from recommendations app: {e}")

print("Import testing complete")