# Use Node.js to build the frontend
FROM node:18 AS frontend-build

WORKDIR /app/frontend
COPY pet-connect-frontend/package*.json ./
RUN npm install
COPY pet-connect-frontend/ ./
RUN npm run build

# Set up Python environment for backend
FROM python:3.9

# Set work directory
WORKDIR /app

# Copy and install backend requirements
COPY pet_connect_backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn whitenoise dj-database-url

# Copy the backend code
COPY pet_connect_backend/ /app/

# Copy the built frontend files to a location Django can serve
COPY --from=frontend-build /app/frontend/build /app/frontend_build

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=pet_connect_backend.settings_production
ENV PORT=8000

# Create a startup script
RUN echo '#!/bin/bash\n\
python manage.py migrate\n\
python manage.py collectstatic --noinput\n\
gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:$PORT\n' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose the port the app runs on
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]