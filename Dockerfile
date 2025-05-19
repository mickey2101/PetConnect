# Use Node.js to build the frontend
FROM node:18 AS frontend-build

WORKDIR /app/frontend
COPY pet-connect-frontend/package*.json ./
RUN npm install
COPY pet-connect-frontend/ ./
RUN npm run build
RUN ls -la build/

# Set up Python environment for backend
FROM python:3.9-slim

# Install project requirements
WORKDIR /app
COPY pet_connect_backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

# Copy the backend code
COPY pet_connect_backend/ /app/

# Create directories for frontend files
RUN mkdir -p /app/frontend_build/static

# Copy the built frontend files
COPY --from=frontend-build /app/frontend/build/ /app/frontend_build/

# Create a local_settings.py file with CSRF fixes
RUN echo "# Local settings - override Django settings" > /app/pet_connect_backend/local_settings.py
RUN echo "import os" >> /app/pet_connect_backend/local_settings.py
RUN echo "import sys" >> /app/pet_connect_backend/local_settings.py
RUN echo "from pathlib import Path" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Print to stderr for debugging" >> /app/pet_connect_backend/local_settings.py
RUN echo "print('Loading local_settings.py', file=sys.stderr)" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Build paths inside the project" >> /app/pet_connect_backend/local_settings.py
RUN echo "BASE_DIR = Path(__file__).resolve().parent.parent" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Debug settings" >> /app/pet_connect_backend/local_settings.py
RUN echo "DEBUG = True" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Set allowed hosts" >> /app/pet_connect_backend/local_settings.py
RUN echo "ALLOWED_HOSTS = ['*', 'petconnect-production-a6f2.up.railway.app']" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# CSRF settings" >> /app/pet_connect_backend/local_settings.py
RUN echo "CSRF_TRUSTED_ORIGINS = [" >> /app/pet_connect_backend/local_settings.py
RUN echo "    'https://petconnect-production-a6f2.up.railway.app'," >> /app/pet_connect_backend/local_settings.py
RUN echo "    'http://petconnect-production-a6f2.up.railway.app'," >> /app/pet_connect_backend/local_settings.py
RUN echo "]" >> /app/pet_connect_backend/local_settings.py
RUN echo "CSRF_COOKIE_SECURE = False  # Set to True when using HTTPS" >> /app/pet_connect_backend/local_settings.py
RUN echo "CSRF_COOKIE_HTTPONLY = False  # Must be False for JavaScript to access it" >> /app/pet_connect_backend/local_settings.py
RUN echo "CSRF_COOKIE_SAMESITE = 'Lax'  # Use 'None' for cross-site requests with Secure=True" >> /app/pet_connect_backend/local_settings.py
RUN echo "CSRF_USE_SESSIONS = False  # Store CSRF token in cookie, not session" >> /app/pet_connect_backend/local_settings.py
RUN echo "CSRF_COOKIE_NAME = 'csrftoken'  # Default name" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Static files settings" >> /app/pet_connect_backend/local_settings.py
RUN echo "STATIC_URL = '/static/'" >> /app/pet_connect_backend/local_settings.py
RUN echo "STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')" >> /app/pet_connect_backend/local_settings.py
RUN echo "STATICFILES_DIRS = [" >> /app/pet_connect_backend/local_settings.py
RUN echo "    os.path.join(BASE_DIR, 'frontend_build', 'static')," >> /app/pet_connect_backend/local_settings.py
RUN echo "]" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Template settings for React" >> /app/pet_connect_backend/local_settings.py
RUN echo "TEMPLATES = [" >> /app/pet_connect_backend/local_settings.py
RUN echo "    {" >> /app/pet_connect_backend/local_settings.py
RUN echo "        'BACKEND': 'django.template.backends.django.DjangoTemplates'," >> /app/pet_connect_backend/local_settings.py
RUN echo "        'DIRS': [" >> /app/pet_connect_backend/local_settings.py
RUN echo "            os.path.join(BASE_DIR, 'frontend_build')," >> /app/pet_connect_backend/local_settings.py
RUN echo "        ]," >> /app/pet_connect_backend/local_settings.py
RUN echo "        'APP_DIRS': True," >> /app/pet_connect_backend/local_settings.py
RUN echo "        'OPTIONS': {" >> /app/pet_connect_backend/local_settings.py
RUN echo "            'context_processors': [" >> /app/pet_connect_backend/local_settings.py
RUN echo "                'django.template.context_processors.debug'," >> /app/pet_connect_backend/local_settings.py
RUN echo "                'django.template.context_processors.request'," >> /app/pet_connect_backend/local_settings.py
RUN echo "                'django.contrib.auth.context_processors.auth'," >> /app/pet_connect_backend/local_settings.py
RUN echo "                'django.contrib.messages.context_processors.messages'," >> /app/pet_connect_backend/local_settings.py
RUN echo "            ]," >> /app/pet_connect_backend/local_settings.py
RUN echo "        }," >> /app/pet_connect_backend/local_settings.py
RUN echo "    }," >> /app/pet_connect_backend/local_settings.py
RUN echo "]" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# CORS settings" >> /app/pet_connect_backend/local_settings.py
RUN echo "CORS_ALLOW_ALL_ORIGINS = True" >> /app/pet_connect_backend/local_settings.py
RUN echo "CORS_ALLOW_CREDENTIALS = True" >> /app/pet_connect_backend/local_settings.py
RUN echo "CORS_ALLOWED_ORIGINS = [" >> /app/pet_connect_backend/local_settings.py
RUN echo "    'https://petconnect-production-a6f2.up.railway.app'," >> /app/pet_connect_backend/local_settings.py
RUN echo "    'http://petconnect-production-a6f2.up.railway.app'," >> /app/pet_connect_backend/local_settings.py
RUN echo "    'http://localhost:3000'," >> /app/pet_connect_backend/local_settings.py
RUN echo "]" >> /app/pet_connect_backend/local_settings.py

# Import local_settings at the end of the main settings file
RUN echo "\n# Import local settings\ntry:\n    from .local_settings import *\nexcept ImportError:\n    pass" >> /app/pet_connect_backend/settings.py

# Add test URL and catchall for React
RUN echo "\n# Add test endpoints" >> /app/pet_connect_backend/urls.py
RUN echo "from django.urls import path, re_path" >> /app/pet_connect_backend/urls.py
RUN echo "from django.views.generic import TemplateView" >> /app/pet_connect_backend/urls.py
RUN echo "from django.http import HttpResponse, JsonResponse" >> /app/pet_connect_backend/urls.py
RUN echo "" >> /app/pet_connect_backend/urls.py
RUN echo "def test_view(request):" >> /app/pet_connect_backend/urls.py
RUN echo "    return HttpResponse('<h1>Django is running!</h1><p>Test view is working.</p>')" >> /app/pet_connect_backend/urls.py
RUN echo "" >> /app/pet_connect_backend/urls.py
RUN echo "def csrf_debug(request):" >> /app/pet_connect_backend/urls.py
RUN echo "    from django.middleware.csrf import get_token" >> /app/pet_connect_backend/urls.py
RUN echo "    csrf_token = get_token(request)" >> /app/pet_connect_backend/urls.py
RUN echo "    return JsonResponse({" >> /app/pet_connect_backend/urls.py
RUN echo "        'csrf_token': csrf_token," >> /app/pet_connect_backend/urls.py
RUN echo "        'csrf_cookie': request.COOKIES.get('csrftoken', None)," >> /app/pet_connect_backend/urls.py
RUN echo "        'request_host': request.get_host()," >> /app/pet_connect_backend/urls.py
RUN echo "        'request_origin': request.META.get('HTTP_ORIGIN', None)," >> /app/pet_connect_backend/urls.py
RUN echo "        'trusted_origins': getattr(from django.conf import settings; settings, 'CSRF_TRUSTED_ORIGINS', [])," >> /app/pet_connect_backend/urls.py
RUN echo "    })" >> /app/pet_connect_backend/urls.py
RUN echo "" >> /app/pet_connect_backend/urls.py
RUN echo "# Fix the custom 403 CSRF handler" >> /app/pet_connect_backend/urls.py
RUN echo "from django.views.decorators.csrf import requires_csrf_token" >> /app/pet_connect_backend/urls.py
RUN echo "from django.http import HttpResponseForbidden" >> /app/pet_connect_backend/urls.py
RUN echo "@requires_csrf_token" >> /app/pet_connect_backend/urls.py
RUN echo "def csrf_failure(request, reason=''):" >> /app/pet_connect_backend/urls.py
RUN echo "    return HttpResponseForbidden(" >> /app/pet_connect_backend/urls.py
RUN echo "        f'<h1>CSRF Verification Failed</h1><p>Reason: {reason}</p>" >> /app/pet_connect_backend/urls.py
RUN echo "        <p>Host: {request.get_host()}</p>" >> /app/pet_connect_backend/urls.py
RUN echo "        <p>Origin: {request.META.get(\"HTTP_ORIGIN\", \"None\")}</p>'" >> /app/pet_connect_backend/urls.py
RUN echo "    )" >> /app/pet_connect_backend/urls.py
RUN echo "" >> /app/pet_connect_backend/urls.py
RUN echo "urlpatterns += [" >> /app/pet_connect_backend/urls.py
RUN echo "    path('django-test/', test_view, name='test_view')," >> /app/pet_connect_backend/urls.py
RUN echo "    path('csrf-debug/', csrf_debug, name='csrf_debug')," >> /app/pet_connect_backend/urls.py
RUN echo "    re_path(r'^(?!api/|admin/).*$', TemplateView.as_view(template_name='index.html'))," >> /app/pet_connect_backend/urls.py
RUN echo "]" >> /app/pet_connect_backend/urls.py

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV DEBUG=1
ENV SECRET_KEY="django-insecure-8z6+v$1*v3l5&vk*dqpq8+rsz#65zn$1486v27gdh!v6!9(89y"

# Create a startup script
RUN echo "#!/bin/bash" > /app/start.sh
RUN echo "echo \"Frontend build files:\"" >> /app/start.sh
RUN echo "ls -la /app/frontend_build/ || echo \"No frontend_build directory\"" >> /app/start.sh
RUN echo "echo \"Starting migrations...\"" >> /app/start.sh
RUN echo "python manage.py migrate" >> /app/start.sh
RUN echo "echo \"Collecting static files...\"" >> /app/start.sh
RUN echo "python manage.py collectstatic --noinput" >> /app/start.sh
RUN echo "echo \"Starting server...\"" >> /app/start.sh
RUN echo "gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:\$PORT --log-level debug" >> /app/start.sh

RUN chmod +x /app/start.sh

# Expose the port
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]