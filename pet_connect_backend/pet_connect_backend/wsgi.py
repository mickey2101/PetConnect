"""
WSGI config for pet_connect_backend project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Check if we're in production
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'pet_connect_backend.settings_production':
    # Load production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_connect_backend.settings_production')
    # Set root URL conf to use production URLs
    os.environ.setdefault('DJANGO_ROOT_URLCONF', 'pet_connect_backend.urls_production')
else:
    # Use default settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_connect_backend.settings')

application = get_wsgi_application()