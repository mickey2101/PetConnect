# Use two-stage build with separate containers for frontend and backend

# Stage 1: Build the React frontend
FROM node:18 AS frontend-build
WORKDIR /frontend
COPY pet-connect-frontend/package*.json ./
RUN npm install
COPY pet-connect-frontend/ ./
# Build the React app
RUN npm run build

# Stage 2: Set up the Django backend
FROM python:3.9-slim
WORKDIR /app

# Install backend requirements
COPY pet_connect_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the backend code
COPY pet_connect_backend/ .

# Copy the built frontend files to a static directory
COPY --from=frontend-build /frontend/build /app/frontend_build

# Create a simple WSGI server script
RUN echo 'from pet_connect_backend.wsgi import application' > /app/wsgi.py

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=1
ENV PORT=8000

# Add CORS and allowed hosts settings
RUN echo '# Production settings\nDEBUG = True\nALLOWED_HOSTS = ["*"]\nCORS_ALLOW_ALL_ORIGINS = True' >> /app/pet_connect_backend/settings.py

# Create a simple startup script
RUN echo '#!/bin/bash\necho "Starting Django server on port $PORT"\npython manage.py migrate\ngunicorn wsgi:application --bind 0.0.0.0:$PORT' > /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]