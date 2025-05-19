# Use Node.js to build the frontend
FROM node:18 AS frontend-build

WORKDIR /app/frontend
COPY pet-connect-frontend/package*.json ./
RUN npm install
COPY pet-connect-frontend/ ./
RUN npm run build
# Debug - list the build directory structure
RUN ls -la build/

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

# Create the frontend_build directory
RUN mkdir -p /app/frontend_build

# Copy the built frontend files to a location Django can serve
COPY --from=frontend-build /app/frontend/build/ /app/frontend_build/
# Debug - list the copied frontend files
RUN ls -la /app/frontend_build/

# Create a simple index.html file as a fallback
RUN echo '<html><body><h1>Pet Connect</h1><p>This is a fallback page. If you see this, the React app failed to load.</p></body></html>' > /app/frontend_build/index.html

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=pet_connect_backend.settings_production
ENV PORT=8000

# Create a verbose startup script
RUN echo '#!/bin/bash\n\
echo "Current directory: $(pwd)"\n\
echo "Listing directory contents:"\n\
ls -la\n\
echo "Listing frontend_build directory:"\n\
ls -la frontend_build\n\
echo "Starting migrations..."\n\
python manage.py migrate\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
echo "Starting server..."\n\
gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:$PORT --log-level debug\n' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose the port the app runs on
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]