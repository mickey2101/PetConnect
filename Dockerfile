# Use Node.js to build the frontend
FROM node:18 AS frontend-build

WORKDIR /app/frontend
COPY pet-connect-frontend/package*.json ./
RUN npm install
COPY pet-connect-frontend/ ./
RUN npm run build
# Debug frontend build output
RUN ls -la build/
RUN ls -la build/static/ || echo "No static directory found"

# Set up Python environment for backend
FROM python:3.9-slim

# Install project requirements
WORKDIR /app
COPY pet_connect_backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

# Copy the backend code
COPY pet_connect_backend/ /app/

# Create directory for frontend files
RUN mkdir -p /app/frontend_build/static

# Copy the built frontend files
COPY --from=frontend-build /app/frontend/build/ /app/frontend_build/

# Create a settings override file
RUN echo "# Frontend settings" > /app/pet_connect_backend/frontend_settings.py
RUN echo "import os" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "from pathlib import Path" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "# Debug mode ON" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "DEBUG = True" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "# Allow all hosts" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "ALLOWED_HOSTS = ['*', 'petconnect-production-a6f2.up.railway.app']" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "# CSRF settings" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "CSRF_TRUSTED_ORIGINS = ['https://petconnect-production-a6f2.up.railway.app']" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "# Base directory path" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "BASE_DIR = Path(__file__).resolve().parent.parent" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "# Static files configuration" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "STATIC_URL = '/static/'" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "STATICFILES_DIRS = [" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    os.path.join(BASE_DIR, 'frontend_build', 'static')," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "]" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "# Whitenoise configuration" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "MIDDLEWARE = [" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    'django.middleware.security.SecurityMiddleware'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    'whitenoise.middleware.WhiteNoiseMiddleware'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    'django.contrib.sessions.middleware.SessionMiddleware'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    'corsheaders.middleware.CorsMiddleware'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    'django.middleware.common.CommonMiddleware'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    'django.middleware.csrf.CsrfViewMiddleware'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    'django.contrib.auth.middleware.AuthenticationMiddleware'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    'django.contrib.messages.middleware.MessageMiddleware'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    'django.middleware.clickjacking.XFrameOptionsMiddleware'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "]" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "# Template configuration to find React app" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "TEMPLATES = [" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    {" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "        'BACKEND': 'django.template.backends.django.DjangoTemplates'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "        'DIRS': [" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "            os.path.join(BASE_DIR, 'frontend_build')," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "        ]," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "        'APP_DIRS': True," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "        'OPTIONS': {" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "            'context_processors': [" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "                'django.template.context_processors.debug'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "                'django.template.context_processors.request'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "                'django.contrib.auth.context_processors.auth'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "                'django.contrib.messages.context_processors.messages'," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "            ]," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "        }," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "    }," >> /app/pet_connect_backend/frontend_settings.py
RUN echo "]" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "# CORS settings" >> /app/pet_connect_backend/frontend_settings.py
RUN echo "CORS_ALLOW_ALL_ORIGINS = True" >> /app/pet_connect_backend/frontend_settings.py

# Create a frontend URLs file that adds the React catch-all route
RUN echo "# Frontend URLs" > /app/frontend_urls.py
RUN echo "from django.urls import path, re_path" >> /app/frontend_urls.py
RUN echo "from django.views.generic import TemplateView" >> /app/frontend_urls.py
RUN echo "from django.http import HttpResponse" >> /app/frontend_urls.py
RUN echo "" >> /app/frontend_urls.py
RUN echo "def frontend_debug(request):" >> /app/frontend_urls.py
RUN echo "    import os" >> /app/frontend_urls.py
RUN echo "    template_dirs = []" >> /app/frontend_urls.py
RUN echo "    from django.conf import settings" >> /app/frontend_urls.py
RUN echo "    for template in settings.TEMPLATES:" >> /app/frontend_urls.py
RUN echo "        template_dirs.extend(template['DIRS'])" >> /app/frontend_urls.py
RUN echo "    frontend_dir = os.path.join(settings.BASE_DIR, 'frontend_build')" >> /app/frontend_urls.py
RUN echo "    index_path = os.path.join(frontend_dir, 'index.html')" >> /app/frontend_urls.py
RUN echo "    static_dirs = getattr(settings, 'STATICFILES_DIRS', [])" >> /app/frontend_urls.py
RUN echo "    debug_info = {" >> /app/frontend_urls.py
RUN echo "        'template_dirs': template_dirs," >> /app/frontend_urls.py
RUN echo "        'frontend_dir': frontend_dir," >> /app/frontend_urls.py
RUN echo "        'frontend_dir_exists': os.path.exists(frontend_dir)," >> /app/frontend_urls.py
RUN echo "        'index_path': index_path," >> /app/frontend_urls.py
RUN echo "        'index_exists': os.path.exists(index_path)," >> /app/frontend_urls.py
RUN echo "        'static_dirs': static_dirs," >> /app/frontend_urls.py
RUN echo "        'frontend_contents': os.listdir(frontend_dir) if os.path.exists(frontend_dir) else []," >> /app/frontend_urls.py
RUN echo "    }" >> /app/frontend_urls.py
RUN echo "    return HttpResponse('<pre>' + str(debug_info) + '</pre>')" >> /app/frontend_urls.py
RUN echo "" >> /app/frontend_urls.py
RUN echo "urlpatterns = [" >> /app/frontend_urls.py
RUN echo "    path('frontend-debug/', frontend_debug)," >> /app/frontend_urls.py
RUN echo "    # This will serve the React frontend for all non-API routes" >> /app/frontend_urls.py
RUN echo "    re_path(r'^(?!api/|admin/).*$', TemplateView.as_view(template_name='index.html'))," >> /app/frontend_urls.py
RUN echo "]" >> /app/frontend_urls.py

# Import the frontend settings and URLs in the right order
RUN echo "\n# Import frontend settings\ntry:\n    from .frontend_settings import *\nexcept ImportError:\n    pass" >> /app/pet_connect_backend/settings.py
RUN echo "\n# Import frontend URLs\nimport sys\nsys.path.append('/app')\nfrom frontend_urls import urlpatterns as frontend_urlpatterns\nurlpatterns += frontend_urlpatterns" >> /app/pet_connect_backend/urls.py

# Create a simple placeholder index.html in case the React build is missing
RUN echo "<!DOCTYPE html>" > /app/frontend_build/index.html
RUN echo "<html>" >> /app/frontend_build/index.html
RUN echo "<head>" >> /app/frontend_build/index.html
RUN echo "    <title>Pet Connect</title>" >> /app/frontend_build/index.html
RUN echo "    <style>" >> /app/frontend_build/index.html
RUN echo "        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }" >> /app/frontend_build/index.html
RUN echo "        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }" >> /app/frontend_build/index.html
RUN echo "        h1 { color: #3c8dbc; }" >> /app/frontend_build/index.html
RUN echo "    </style>" >> /app/frontend_build/index.html
RUN echo "</head>" >> /app/frontend_build/index.html
RUN echo "<body>" >> /app/frontend_build/index.html
RUN echo "    <div class=\"container\">" >> /app/frontend_build/index.html
RUN echo "        <h1>Pet Connect</h1>" >> /app/frontend_build/index.html
RUN echo "        <p>This is a replacement index.html file. If you see this page, it means the React frontend build wasn't correctly copied.</p>" >> /app/frontend_build/index.html
RUN echo "        <p>You can access the backend API at these endpoints:</p>" >> /app/frontend_build/index.html
RUN echo "        <ul>" >> /app/frontend_build/index.html
RUN echo "            <li><a href=\"/api/animals/\">/api/animals/</a></li>" >> /app/frontend_build/index.html
RUN echo "            <li><a href=\"/api/users/\">/api/users/</a></li>" >> /app/frontend_build/index.html
RUN echo "            <li><a href=\"/api/recommendations/\">/api/recommendations/</a></li>" >> /app/frontend_build/index.html
RUN echo "            <li><a href=\"/admin/\">/admin/</a></li>" >> /app/frontend_build/index.html
RUN echo "        </ul>" >> /app/frontend_build/index.html
RUN echo "        <p>Check the <a href=\"/frontend-debug/\">frontend debug page</a> for more information.</p>" >> /app/frontend_build/index.html
RUN echo "    </div>" >> /app/frontend_build/index.html
RUN echo "</body>" >> /app/frontend_build/index.html
RUN echo "</html>" >> /app/frontend_build/index.html

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV DEBUG=1

# Create a startup script with better diagnostics
RUN echo "#!/bin/bash" > /app/start.sh
RUN echo "echo \"Directory structure:\"" >> /app/start.sh
RUN echo "find /app -maxdepth 2 -type d | sort" >> /app/start.sh
RUN echo "echo \"\nFrontend build directory:\"" >> /app/start.sh
RUN echo "ls -la /app/frontend_build/" >> /app/start.sh
RUN echo "echo \"\nStatic files directory:\"" >> /app/start.sh
RUN echo "ls -la /app/frontend_build/static/ || echo \"No static directory found\"" >> /app/start.sh
RUN echo "echo \"\nStarting migrations...\"" >> /app/start.sh
RUN echo "python manage.py migrate" >> /app/start.sh
RUN echo "echo \"\nCollecting static files...\"" >> /app/start.sh
RUN echo "python manage.py collectstatic --noinput" >> /app/start.sh
RUN echo "echo \"\nStarting server...\"" >> /app/start.sh
RUN echo "gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:\$PORT --log-level debug" >> /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]