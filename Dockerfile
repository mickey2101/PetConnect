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

# Create directory for frontend files and copy the built frontend
RUN mkdir -p /app/frontend_build/static
COPY --from=frontend-build /app/frontend/build/ /app/frontend_build/

# Create configuration files with one RUN command to reduce layers
RUN echo '# Frontend settings\n\
import os\n\
from pathlib import Path\n\
\n\
# Debug mode ON\n\
DEBUG = True\n\
\n\
# Allow all hosts\n\
ALLOWED_HOSTS = ["*", "petconnect-production-a6f2.up.railway.app"]\n\
\n\
# CSRF settings\n\
CSRF_TRUSTED_ORIGINS = ["https://petconnect-production-a6f2.up.railway.app"]\n\
\n\
# Base directory path\n\
BASE_DIR = Path(__file__).resolve().parent.parent\n\
\n\
# Static files configuration\n\
STATIC_URL = "/static/"\n\
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")\n\
STATICFILES_DIRS = [\n\
    os.path.join(BASE_DIR, "frontend_build", "static"),\n\
]\n\
\n\
# Whitenoise configuration\n\
MIDDLEWARE = [\n\
    "django.middleware.security.SecurityMiddleware",\n\
    "whitenoise.middleware.WhiteNoiseMiddleware",\n\
    "django.contrib.sessions.middleware.SessionMiddleware",\n\
    "corsheaders.middleware.CorsMiddleware",\n\
    "django.middleware.common.CommonMiddleware",\n\
    "django.middleware.csrf.CsrfViewMiddleware",\n\
    "django.contrib.auth.middleware.AuthenticationMiddleware",\n\
    "django.contrib.messages.middleware.MessageMiddleware",\n\
    "django.middleware.clickjacking.XFrameOptionsMiddleware",\n\
]\n\
\n\
# Template configuration to find React app\n\
TEMPLATES = [\n\
    {\n\
        "BACKEND": "django.template.backends.django.DjangoTemplates",\n\
        "DIRS": [\n\
            os.path.join(BASE_DIR, "frontend_build"),\n\
        ],\n\
        "APP_DIRS": True,\n\
        "OPTIONS": {\n\
            "context_processors": [\n\
                "django.template.context_processors.debug",\n\
                "django.template.context_processors.request",\n\
                "django.contrib.auth.context_processors.auth",\n\
                "django.contrib.messages.context_processors.messages",\n\
            ],\n\
        },\n\
    },\n\
]\n\
\n\
# CORS settings\n\
CORS_ALLOW_ALL_ORIGINS = True\n\
' > /app/pet_connect_backend/frontend_settings.py && \
echo '# Frontend URLs\n\
from django.urls import path, re_path\n\
from django.views.generic import TemplateView\n\
from django.http import HttpResponse\n\
\n\
def frontend_debug(request):\n\
    import os\n\
    template_dirs = []\n\
    from django.conf import settings\n\
    for template in settings.TEMPLATES:\n\
        template_dirs.extend(template["DIRS"])\n\
    frontend_dir = os.path.join(settings.BASE_DIR, "frontend_build")\n\
    index_path = os.path.join(frontend_dir, "index.html")\n\
    static_dirs = getattr(settings, "STATICFILES_DIRS", [])\n\
    debug_info = {\n\
        "template_dirs": template_dirs,\n\
        "frontend_dir": frontend_dir,\n\
        "frontend_dir_exists": os.path.exists(frontend_dir),\n\
        "index_path": index_path,\n\
        "index_exists": os.path.exists(index_path),\n\
        "static_dirs": static_dirs,\n\
        "frontend_contents": os.listdir(frontend_dir) if os.path.exists(frontend_dir) else [],\n\
    }\n\
    return HttpResponse("<pre>" + str(debug_info) + "</pre>")\n\
\n\
urlpatterns = [\n\
    path("frontend-debug/", frontend_debug),\n\
    # This will serve the React frontend for all non-API routes\n\
    re_path(r"^(?!api/|admin/).*$", TemplateView.as_view(template_name="index.html")),\n\
]\n\
' > /app/frontend_urls.py && \
echo '<!DOCTYPE html>\n\
<html>\n\
<head>\n\
    <title>Pet Connect</title>\n\
    <style>\n\
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }\n\
        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }\n\
        h1 { color: #3c8dbc; }\n\
    </style>\n\
</head>\n\
<body>\n\
    <div class="container">\n\
        <h1>Pet Connect</h1>\n\
        <p>This is a replacement index.html file. If you see this page, it means the React frontend build was not correctly copied.</p>\n\
        <p>You can access the backend API at these endpoints:</p>\n\
        <ul>\n\
            <li><a href="/api/animals/">/api/animals/</a></li>\n\
            <li><a href="/api/users/">/api/users/</a></li>\n\
            <li><a href="/api/recommendations/">/api/recommendations/</a></li>\n\
            <li><a href="/admin/">/admin/</a></li>\n\
        </ul>\n\
        <p>Check the <a href="/frontend-debug/">frontend debug page</a> for more information.</p>\n\
    </div>\n\
</body>\n\
</html>\n\
' > /app/frontend_build/index.html

# Update settings and URLs files in one command
RUN echo "\n# Import frontend settings\ntry:\n    from .frontend_settings import *\nexcept ImportError:\n    pass" >> /app/pet_connect_backend/settings.py && \
echo "\n# Import frontend URLs\nimport sys\nsys.path.append('/app')\nfrom frontend_urls import urlpatterns as frontend_urlpatterns\nurlpatterns += frontend_urlpatterns" >> /app/pet_connect_backend/urls.py

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DEBUG=1

# Create a startup script with better diagnostics
RUN echo '#!/bin/bash\n\
echo "Directory structure:"\n\
find /app -maxdepth 2 -type d | sort\n\
echo "\nFrontend build directory:"\n\
ls -la /app/frontend_build/\n\
echo "\nStatic files directory:"\n\
ls -la /app/frontend_build/static/ || echo "No static directory found"\n\
echo "\nStarting migrations..."\n\
python manage.py migrate\n\
echo "\nCollecting static files..."\n\
python manage.py collectstatic --noinput\n\
echo "\nStarting server..."\n\
gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:$PORT --log-level debug\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]