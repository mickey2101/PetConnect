# Set up Python environment for backend only
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Copy and install backend requirements
COPY pet_connect_backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn whitenoise

# Copy the backend code
COPY pet_connect_backend/ /app/

# Create a simple backup index view for testing
RUN mkdir -p /app/pet_connect_backend
RUN echo "from django.http import HttpResponse\n\ndef test_view(request):\n    return HttpResponse('<h1>Pet Connect Test</h1><p>Django is working!</p>')" >> /app/pet_connect_backend/views.py

# Add a test URL to main urls.py
RUN echo "# Added test URL\nfrom django.http import HttpResponse\n\ndef test_view(request):\n    return HttpResponse('<h1>Pet Connect Test</h1><p>Django is working!</p>')\n\n# Add this to urlpatterns\nurlpatterns.append(path('simple-test/', test_view, name='simple_test'))" >> /app/pet_connect_backend/urls.py

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=1
ENV PORT=8000

# Create a verbose startup script for debugging
RUN echo '#!/bin/bash\n\
echo "Current directory: $(pwd)"\n\
echo "Listing Python files:"\n\
find . -name "*.py" | grep -E "urls|wsgi|settings"\n\
echo "Starting migrations..."\n\
python manage.py migrate\n\
echo "Starting server with DEBUG=1..."\n\
gunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:$PORT --log-level debug\n' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose the port the app runs on
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]