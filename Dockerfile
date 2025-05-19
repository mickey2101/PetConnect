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

# Create a local_settings.py file to override settings
RUN echo "# local_settings.py - Override settings\n\
ALLOWED_HOSTS = ['*', 'petconnect-production-a6f2.up.railway.app']\n\
DEBUG = True\n\
\n\
# Configure templates to find the React app\n\
import os\n\
TEMPLATES[0]['DIRS'] = [\n\
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend_build'),\n\
]\n\
\n\
# Configure static files\n\
STATIC_URL = '/static/'\n\
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'staticfiles')\n\
STATICFILES_DIRS = [\n\
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend_build', 'static'),\n\
]\n\
\n\
# Add whitenoise middleware for static files\n\
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:\n\
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')\n\
\n\
# URL Configuration to serve React frontend for all non-API routes\n\
from django.urls import re_path\n\
from django.views.generic import TemplateView\n\
from django.urls import path\n\
from pet_connect_backend.urls import urlpatterns\n\
\n\
# Add catch-all route for React frontend\n\
urlpatterns += [\n\
    re_path(r'^(?!api/|admin/).*$', TemplateView.as_view(template_name='index.html')),\n\
]\n\
" > /app/pet_connect_backend/local_settings.py

# Import local_settings at the end of the main settings file
RUN echo "\n# Import local settings\ntry:\n    from .local_settings import *\nexcept ImportError:\n    pass" >> /app/pet_connect_backend/settings.py

# Create a simple test index.html in case React build fails
RUN mkdir -p /app/frontend_build
RUN echo '<!DOCTYPE html>\n\
<html>\n\
<head>\n\
    <title>Pet Connect</title>\n\
</head>\n\
<body>\n\
    <h1>Pet Connect</h1>\n\
    <p>This is a backup index.html file. If you see this, the React build wasn\'t properly included.</p>\n\
    <p>Try visiting <a href="/admin/">/admin/</a> or <a href="/api/animals/">/api/animals/</a> to verify the backend is working.</p>\n\
</body>\n\
</html>' > /app/frontend_build/index.html

# Create a simple test view
RUN echo "from django.http import HttpResponse\n\ndef test_view(request):\n    return HttpResponse('<h1>Django is running!</h1><p>This test view is working.</p>')" > /app/pet_connect_backend/test_views.py

# Add test URL to main URLs file
RUN echo "\n# Import test view\nfrom pet_connect_backend.test_views import test_view\n\n# Add test URL\nurlpatterns.append(path('django-test/', test_view, name='test_view'))" >> /app/pet_connect_backend/urls.py

# Copy the built frontend files
COPY --from=frontend-build /app/frontend/build/ /app/frontend_build/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Create a verbose startup script
RUN echo '#!/bin/bash\n\
echo "Directory structure:"\n\
find . -type d | sort\n\
echo "\nFrontend files:"\n\
ls -la frontend_build/\n\
echo "\nStarting migrations..."\n\
python manage.py migrate\n\
echo "\nCollecting static files..."\n\
python manage.py collectstatic --noinput\n\
echo "\nStarting Django server..."\n\
gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:$PORT --log-level debug\n' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose the port
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]