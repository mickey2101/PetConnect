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
RUN echo "# local_settings.py - Override settings" > /app/pet_connect_backend/local_settings.py
RUN echo "ALLOWED_HOSTS = ['*', 'petconnect-production-a6f2.up.railway.app']" >> /app/pet_connect_backend/local_settings.py
RUN echo "DEBUG = True" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Configure templates to find the React app" >> /app/pet_connect_backend/local_settings.py
RUN echo "import os" >> /app/pet_connect_backend/local_settings.py
RUN echo "TEMPLATES[0]['DIRS'] = [" >> /app/pet_connect_backend/local_settings.py
RUN echo "    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend_build')," >> /app/pet_connect_backend/local_settings.py
RUN echo "]" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Configure static files" >> /app/pet_connect_backend/local_settings.py
RUN echo "STATIC_URL = '/static/'" >> /app/pet_connect_backend/local_settings.py
RUN echo "STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'staticfiles')" >> /app/pet_connect_backend/local_settings.py
RUN echo "STATICFILES_DIRS = [" >> /app/pet_connect_backend/local_settings.py
RUN echo "    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend_build', 'static')," >> /app/pet_connect_backend/local_settings.py
RUN echo "]" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Add whitenoise middleware for static files" >> /app/pet_connect_backend/local_settings.py
RUN echo "if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:" >> /app/pet_connect_backend/local_settings.py
RUN echo "    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# URL Configuration to serve React frontend for all non-API routes" >> /app/pet_connect_backend/local_settings.py
RUN echo "from django.urls import re_path" >> /app/pet_connect_backend/local_settings.py
RUN echo "from django.views.generic import TemplateView" >> /app/pet_connect_backend/local_settings.py
RUN echo "from django.urls import path" >> /app/pet_connect_backend/local_settings.py
RUN echo "from pet_connect_backend.urls import urlpatterns" >> /app/pet_connect_backend/local_settings.py
RUN echo "" >> /app/pet_connect_backend/local_settings.py
RUN echo "# Add catch-all route for React frontend" >> /app/pet_connect_backend/local_settings.py
RUN echo "urlpatterns += [" >> /app/pet_connect_backend/local_settings.py
RUN echo "    re_path(r'^(?!api/|admin/).*$', TemplateView.as_view(template_name='index.html'))," >> /app/pet_connect_backend/local_settings.py
RUN echo "]" >> /app/pet_connect_backend/local_settings.py

# Import local_settings at the end of the main settings file
RUN echo "\n# Import local settings\ntry:\n    from .local_settings import *\nexcept ImportError:\n    pass" >> /app/pet_connect_backend/settings.py

# Create a simple test index.html in case React build fails
RUN mkdir -p /app/frontend_build
# Create index.html safely by writing to a file using multiple echo commands
RUN echo "<!DOCTYPE html>" > /app/frontend_build/index.html
RUN echo "<html>" >> /app/frontend_build/index.html
RUN echo "<head>" >> /app/frontend_build/index.html
RUN echo "    <title>Pet Connect</title>" >> /app/frontend_build/index.html
RUN echo "</head>" >> /app/frontend_build/index.html
RUN echo "<body>" >> /app/frontend_build/index.html
RUN echo "    <h1>Pet Connect</h1>" >> /app/frontend_build/index.html
RUN echo "    <p>This is a backup index.html file. If you see this, the React build was not properly included.</p>" >> /app/frontend_build/index.html
RUN echo "    <p>Try visiting <a href=\"/admin/\">/admin/</a> or <a href=\"/api/animals/\">/api/animals/</a> to verify the backend is working.</p>" >> /app/frontend_build/index.html
RUN echo "</body>" >> /app/frontend_build/index.html
RUN echo "</html>" >> /app/frontend_build/index.html

# Create a simple test view
RUN echo "from django.http import HttpResponse" > /app/pet_connect_backend/test_views.py
RUN echo "" >> /app/pet_connect_backend/test_views.py
RUN echo "def test_view(request):" >> /app/pet_connect_backend/test_views.py
RUN echo "    return HttpResponse('<h1>Django is running!</h1><p>This test view is working.</p>')" >> /app/pet_connect_backend/test_views.py

# Add test URL to main URLs file
RUN echo "\n# Import test view" >> /app/pet_connect_backend/urls.py
RUN echo "from pet_connect_backend.test_views import test_view" >> /app/pet_connect_backend/urls.py
RUN echo "\n# Add test URL" >> /app/pet_connect_backend/urls.py
RUN echo "urlpatterns.append(path('django-test/', test_view, name='test_view'))" >> /app/pet_connect_backend/urls.py

# Copy the built frontend files
COPY --from=frontend-build /app/frontend/build/ /app/frontend_build/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Create a verbose startup script
RUN echo "#!/bin/bash" > /app/start.sh
RUN echo "echo \"Directory structure:\"" >> /app/start.sh
RUN echo "find . -type d | sort" >> /app/start.sh
RUN echo "echo \"\nFrontend files:\"" >> /app/start.sh
RUN echo "ls -la frontend_build/" >> /app/start.sh
RUN echo "echo \"\nStarting migrations...\"" >> /app/start.sh
RUN echo "python manage.py migrate" >> /app/start.sh
RUN echo "echo \"\nCollecting static files...\"" >> /app/start.sh
RUN echo "python manage.py collectstatic --noinput" >> /app/start.sh
RUN echo "echo \"\nStarting Django server...\"" >> /app/start.sh
RUN echo "gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:\$PORT --log-level debug" >> /app/start.sh

RUN chmod +x /app/start.sh

# Expose the port
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]