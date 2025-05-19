# Use a simple Python image
FROM python:3.9-slim

# Install Django and dependencies
WORKDIR /app
COPY pet_connect_backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

# Copy only the backend code (simplify for debugging)
COPY pet_connect_backend/ /app/

# Create a bare-bones debugging settings file
RUN echo "# Debugging settings" > /app/pet_connect_backend/debug_settings.py
RUN echo "import os" >> /app/pet_connect_backend/debug_settings.py
RUN echo "from pathlib import Path" >> /app/pet_connect_backend/debug_settings.py
RUN echo "" >> /app/pet_connect_backend/debug_settings.py
RUN echo "# Debug mode ON" >> /app/pet_connect_backend/debug_settings.py
RUN echo "DEBUG = True" >> /app/pet_connect_backend/debug_settings.py
RUN echo "" >> /app/pet_connect_backend/debug_settings.py
RUN echo "# Allow all hosts" >> /app/pet_connect_backend/debug_settings.py
RUN echo "ALLOWED_HOSTS = ['*']" >> /app/pet_connect_backend/debug_settings.py
RUN echo "" >> /app/pet_connect_backend/debug_settings.py
RUN echo "# Set CSRF trusted origins" >> /app/pet_connect_backend/debug_settings.py
RUN echo "CSRF_TRUSTED_ORIGINS = ['https://petconnect-production-a6f2.up.railway.app']" >> /app/pet_connect_backend/debug_settings.py
RUN echo "" >> /app/pet_connect_backend/debug_settings.py
RUN echo "# Enable detailed error reporting" >> /app/pet_connect_backend/debug_settings.py
RUN echo "LOGGING = {" >> /app/pet_connect_backend/debug_settings.py
RUN echo "    'version': 1," >> /app/pet_connect_backend/debug_settings.py
RUN echo "    'disable_existing_loggers': False," >> /app/pet_connect_backend/debug_settings.py
RUN echo "    'formatters': {" >> /app/pet_connect_backend/debug_settings.py
RUN echo "        'verbose': {" >> /app/pet_connect_backend/debug_settings.py
RUN echo "            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}'," >> /app/pet_connect_backend/debug_settings.py
RUN echo "            'style': '{'," >> /app/pet_connect_backend/debug_settings.py
RUN echo "        }," >> /app/pet_connect_backend/debug_settings.py
RUN echo "    }," >> /app/pet_connect_backend/debug_settings.py
RUN echo "    'handlers': {" >> /app/pet_connect_backend/debug_settings.py
RUN echo "        'console': {" >> /app/pet_connect_backend/debug_settings.py
RUN echo "            'level': 'DEBUG'," >> /app/pet_connect_backend/debug_settings.py
RUN echo "            'class': 'logging.StreamHandler'," >> /app/pet_connect_backend/debug_settings.py
RUN echo "            'formatter': 'verbose'," >> /app/pet_connect_backend/debug_settings.py
RUN echo "        }," >> /app/pet_connect_backend/debug_settings.py
RUN echo "    }," >> /app/pet_connect_backend/debug_settings.py
RUN echo "    'loggers': {" >> /app/pet_connect_backend/debug_settings.py
RUN echo "        'django': {" >> /app/pet_connect_backend/debug_settings.py
RUN echo "            'handlers': ['console']," >> /app/pet_connect_backend/debug_settings.py
RUN echo "            'level': 'DEBUG'," >> /app/pet_connect_backend/debug_settings.py
RUN echo "            'propagate': True," >> /app/pet_connect_backend/debug_settings.py
RUN echo "        }," >> /app/pet_connect_backend/debug_settings.py
RUN echo "    }," >> /app/pet_connect_backend/debug_settings.py
RUN echo "}" >> /app/pet_connect_backend/debug_settings.py

# Add debug settings import to settings.py
RUN echo "\n# Import debug settings\ntry:\n    from .debug_settings import *\nexcept ImportError:\n    pass" >> /app/pet_connect_backend/settings.py

# Create a basic test view
RUN echo "# Add test endpoints" > /app/fix_urls.py
RUN echo "from django.urls import path" >> /app/fix_urls.py
RUN echo "from django.http import HttpResponse, JsonResponse" >> /app/fix_urls.py
RUN echo "" >> /app/fix_urls.py
RUN echo "def debug_view(request):" >> /app/fix_urls.py
RUN echo "    return HttpResponse('<h1>Debug View Working</h1><p>If you see this, the basic Django server is functioning.</p>')" >> /app/fix_urls.py
RUN echo "" >> /app/fix_urls.py
RUN echo "def settings_view(request):" >> /app/fix_urls.py
RUN echo "    from django.conf import settings" >> /app/fix_urls.py
RUN echo "    safe_settings = {}" >> /app/fix_urls.py
RUN echo "    for key in dir(settings):" >> /app/fix_urls.py
RUN echo "        if key.isupper():" >> /app/fix_urls.py
RUN echo "            try:" >> /app/fix_urls.py
RUN echo "                safe_settings[key] = str(getattr(settings, key))" >> /app/fix_urls.py
RUN echo "            except:" >> /app/fix_urls.py
RUN echo "                safe_settings[key] = 'ERROR: Could not convert to string'" >> /app/fix_urls.py
RUN echo "    return JsonResponse(safe_settings)" >> /app/fix_urls.py
RUN echo "" >> /app/fix_urls.py
RUN echo "def error_test(request):" >> /app/fix_urls.py
RUN echo "    # Deliberately cause an error to test error reporting" >> /app/fix_urls.py
RUN echo "    raise Exception('Test exception to check error handling')" >> /app/fix_urls.py
RUN echo "" >> /app/fix_urls.py
RUN echo "new_urlpatterns = [" >> /app/fix_urls.py
RUN echo "    path('debug/', debug_view)," >> /app/fix_urls.py
RUN echo "    path('settings/', settings_view)," >> /app/fix_urls.py
RUN echo "    path('error-test/', error_test)," >> /app/fix_urls.py
RUN echo "]" >> /app/fix_urls.py

# Add the debug URLs to urls.py
RUN echo "\n# Import debug URLs" >> /app/pet_connect_backend/urls.py
RUN echo "import sys" >> /app/pet_connect_backend/urls.py
RUN echo "sys.path.append('/app')" >> /app/pet_connect_backend/urls.py
RUN echo "from fix_urls import new_urlpatterns" >> /app/pet_connect_backend/urls.py
RUN echo "urlpatterns += new_urlpatterns" >> /app/pet_connect_backend/urls.py

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV DEBUG=1

# Create a diagnostic startup script
RUN echo "#!/bin/bash" > /app/start.sh
RUN echo "echo \"Starting bare-bones Django server for debugging...\"" >> /app/start.sh
RUN echo "echo \"Python version: \$(python --version)\"" >> /app/start.sh
RUN echo "echo \"Django version: \$(python -m django --version)\"" >> /app/start.sh
RUN echo "echo \"Running server with DEBUG=1\"" >> /app/start.sh
RUN echo "gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:\$PORT --log-level debug" >> /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]