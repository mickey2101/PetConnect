# Build the React frontend
FROM node:18 AS frontend-build

# Build React app
WORKDIR /app
COPY pet-connect-frontend/package*.json ./
RUN npm install
COPY pet-connect-frontend/ ./
RUN npm run build
RUN ls -la build/

# Set up Django backend
FROM python:3.9-slim

# Install project requirements
WORKDIR /app
COPY pet_connect_backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

# Copy the backend code
COPY pet_connect_backend/ /app/

# Copy the built React app
COPY --from=frontend-build /app/build/ /app/static_react/

# Create a directory for our custom files
RUN mkdir -p /app/custom_files

# Write the debug view file
COPY <<'EOF' /app/custom_files/debug_view.py
from django.http import HttpResponse
import os

def debug_view(request):
    static_dir = '/app/static_react'
    output = f"<h1>Static directory contents</h1>"
    
    if os.path.exists(static_dir):
        files = os.listdir(static_dir)
        output += f"<p>Files in static_react: {len(files)}</p><ul>"
        for file in files:
            file_path = os.path.join(static_dir, file)
            is_dir = os.path.isdir(file_path)
            output += f"<li>{'📁' if is_dir else '📄'} {file}</li>"
            
            # If it's a directory, show its contents too
            if is_dir:
                subfiles = os.listdir(file_path)
                output += "<ul>"
                for subfile in subfiles:
                    output += f"<li>📄 {subfile}</li>"
                output += "</ul>"
        output += "</ul>"
        
        # Check for index.html
        index_path = os.path.join(static_dir, 'index.html')
        if os.path.exists(index_path):
            output += "<p>✅ index.html exists</p>"
            # Show the first 300 chars of index.html
            with open(index_path, 'r') as f:
                content = f.read(300)
                output += f"<p>First 300 chars of index.html:</p><pre>{content}...</pre>"
        else:
            output += "<p>❌ index.html not found!</p>"
    else:
        output += f"<p>❌ Directory {static_dir} does not exist!</p>"
    
    return HttpResponse(output)
EOF

# Write the ReactAppView file
COPY <<'EOF' /app/custom_files/react_app_view.py
from django.views.generic import View
from django.http import HttpResponse, FileResponse
import os

class ReactAppView(View):
    def get(self, request, *args, **kwargs):
        try:
            with open('/app/static_react/index.html', 'rb') as f:
                return HttpResponse(f.read(), content_type='text/html')
        except FileNotFoundError:
            return HttpResponse("React app not found. Check /debug/ for more information.", status=404)

def serve_static(request, path):
    file_path = os.path.join('/app/static_react', path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(open(file_path, 'rb'))
    return HttpResponse(f"File {path} not found", status=404)
EOF

# Write the settings override file
COPY <<'EOF' /app/custom_files/react_settings.py
import os

# Debug mode for development
DEBUG = True

# Allow all hosts
ALLOWED_HOSTS = ['*', 'petconnect-production-a6f2.up.railway.app']

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://petconnect-production-a6f2.up.railway.app',
]

# CORS settings - allow all origins
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Configure whitenoise
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
EOF

# Create URL configuration for React
COPY <<'EOF' /app/custom_files/urls_config.py
from django.urls import path, re_path
import sys
sys.path.append('/app/custom_files')

from debug_view import debug_view
from react_app_view import ReactAppView, serve_static

# URLs to add to the main urlpatterns
urlpatterns = [
    path('debug/', debug_view, name='debug'),
    path('static/<path:path>', serve_static, name='serve_static'),
    re_path(r'^(?!api/|admin/|debug/|static/).*$', ReactAppView.as_view(), name='react_app'),
]
EOF

# Append to urls.py using a file (more reliable than echo)
COPY <<'EOF' /app/custom_files/urls_append.py

# Import URLs from custom config
import sys
sys.path.append('/app/custom_files')
from urls_config import urlpatterns as custom_urlpatterns

# Add the custom URL patterns
urlpatterns += custom_urlpatterns
EOF

# Append to settings.py using a file
COPY <<'EOF' /app/custom_files/settings_append.py

# Import React settings
import sys
sys.path.append('/app/custom_files')
from react_settings import *  # This brings in DEBUG, ALLOWED_HOSTS, etc.
EOF

# Update settings.py and urls.py using cat instead of echo
RUN cat /app/custom_files/urls_append.py >> /app/pet_connect_backend/urls.py
RUN cat /app/custom_files/settings_append.py >> /app/pet_connect_backend/settings.py

# Create a simple startup script using COPY instead of cat
COPY <<'EOF' /app/start.sh
#!/bin/bash
echo "======== DEPLOYMENT INFO ========"
echo "Directory structure:"
find /app -maxdepth 2 -type d | sort
echo ""
echo "Static React directory:"
ls -la /app/static_react/ || echo "No static_react directory!"
echo ""
echo "Starting migrations..."
python manage.py migrate
echo ""
echo "Starting server..."
gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:$PORT --log-level debug
EOF

RUN chmod +x /app/start.sh

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DEBUG=1

EXPOSE 8000

CMD ["/app/start.sh"]