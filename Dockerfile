# Use a simple Python image that can run Django
FROM python:3.9-slim

# Install project requirements
WORKDIR /app
COPY pet_connect_backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

# Copy the backend code
COPY pet_connect_backend/ /app/

# Create a local_settings.py file that will override ALLOWED_HOSTS
RUN echo "# local_settings.py - Override settings\nALLOWED_HOSTS = ['*', 'petconnect-production-a6f2.up.railway.app']\nDEBUG = True" > /app/pet_connect_backend/local_settings.py

# Import local_settings at the end of your main settings file
RUN echo "\n# Import local settings\ntry:\n    from .local_settings import *\nexcept ImportError:\n    pass" >> /app/pet_connect_backend/settings.py

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Create a startup script
RUN echo '#!/bin/bash\necho "Starting Django with ALLOWED_HOSTS=*, petconnect-production-a6f2.up.railway.app"\npython manage.py migrate\npython manage.py collectstatic --noinput\ngunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:$PORT' > /app/start.sh
RUN chmod +x /app/start.sh

# Expose the port
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]