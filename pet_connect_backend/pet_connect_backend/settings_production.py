"""
Production settings for pet_connect_backend project.
"""

import os
from .settings import *

# Set DEBUG to False in production
DEBUG = False

# Allow all hosts - update with your specific domain in production
ALLOWED_HOSTS = ['*']

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configure templates to find the React app
TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'frontend_build')]

# Add staticfiles directories to include React's static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend_build', 'static'),
]

# Add whitenoise middleware for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Update CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    # Add your production frontend URL here or configure via environment variables
    f"https://{os.environ.get('RAILWAY_STATIC_URL', '*')}",
    f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', '*')}",
]

# Update CSRF settings for production
CSRF_TRUSTED_ORIGINS = [
    # Add your production frontend URL here or configure via environment variables
    f"https://{os.environ.get('RAILWAY_STATIC_URL', '*')}",
    f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', '*')}",
]

# Security settings for production
# These can be enabled once you have HTTPS set up
SECURE_SSL_REDIRECT = False  # Set to True with HTTPS
SESSION_COOKIE_SECURE = False  # Set to True with HTTPS
CSRF_COOKIE_SECURE = False  # Set to True with HTTPS

# Set this to True once your site is served with HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Only use HTTPS-only cookies if you're using HTTPS
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Override the secret key with an environment variable
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# Configure logging to output to console for Railway
if 'file' in LOGGING['handlers']:
    LOGGING['handlers']['file']['class'] = 'logging.StreamHandler'
    if 'filename' in LOGGING['handlers']['file']:
        del LOGGING['handlers']['file']['filename']

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')