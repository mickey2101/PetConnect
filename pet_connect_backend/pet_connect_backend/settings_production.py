"""
Production settings for pet_connect_backend project.
"""

import os
from .settings import *

# Set DEBUG to False in production
DEBUG = False

# Allow all hosts - update with your specific domain in production
ALLOWED_HOSTS = ['https://petconnect-production-a6f2.up.railway.app/', '*']

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configure templates to find the React app - try multiple locations
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'frontend_build'),
            '/app/frontend_build',  # Docker absolute path
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Add staticfiles directories to include React's static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend_build', 'static'),
    '/app/frontend_build/static',  # Docker absolute path
]

# Add whitenoise middleware for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Update CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "https://petconnect-production-a6f2.up.railway.app/",
    "http://petconnect-production-3af8.up.railway.app",
    "http://localhost:3000",
]

# Update CSRF settings for production
CSRF_TRUSTED_ORIGINS = [
    "https://petconnect-production-a6f2.up.railway.app/",
    "http://petconnect-production-3af8.up.railway.app",
]

# Disable these security settings initially to debug
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

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

# Make sure STATIC_ROOT is accessible
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]