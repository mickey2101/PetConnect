# Build the React frontend
FROM node:18 AS frontend-build

# Build React app
WORKDIR /app
COPY pet-connect-frontend/package*.json ./
RUN npm install
COPY pet-connect-frontend/ ./
RUN npm run build
RUN ls -la build/

# Set up Django backend
FROM python:3.9-slim

# Install project requirements
WORKDIR /app
COPY pet_connect_backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

# Copy the backend code
COPY pet_connect_backend/ /app/

# Create a directory for React files
RUN mkdir -p /app/react_app

# Copy the built React app
COPY --from=frontend-build /app/build/ /app/react_app/

# Create a simple view for the React app
RUN echo 'from django.http import HttpResponse, FileResponse\nimport os\n\ndef serve_frontend(request, path=""):\n    """Serve React frontend files"""\n    # For the root or any frontend route, serve index.html\n    if not path or not path.startswith("static/"):\n        try:\n            with open("/app/react_app/index.html", "rb") as f:\n                return HttpResponse(f.read(), content_type="text/html")\n        except FileNotFoundError:\n            return HttpResponse("React app not found", status=404)\n    \n    # For static files\n    if path.startswith("static/"):\n        file_path = os.path.join("/app/react_app", path)\n        if os.path.exists(file_path) and os.path.isfile(file_path):\n            return FileResponse(open(file_path, "rb"))\n    \n    return HttpResponse("File not found", status=404)\n\ndef debug(request):\n    """Debug view to check file locations"""\n    react_dir = "/app/react_app"\n    output = "<h1>React App Debug</h1>"\n    \n    if os.path.exists(react_dir):\n        files = os.listdir(react_dir)\n        output += f"<p>Files in react_app: {len(files)}</p><ul>"\n        for f in files:\n            output += f"<li>{f}</li>"\n        output += "</ul>"\n        \n        if "index.html" in files:\n            with open(os.path.join(react_dir, "index.html"), "r") as f:\n                content = f.read(200)\n                output += f"<p>index.html preview:</p><pre>{content}...</pre>"\n    else:\n        output += "<p>React app directory not found</p>"\n    \n    return HttpResponse(output)' > /app/react_view.py

# Add the URLs for the React app
RUN echo '\n# React Frontend URLs\nfrom django.urls import path, re_path\nimport sys\nsys.path.append("/app")\nfrom react_view import serve_frontend, debug\n\n# Add debug URL\nurlpatterns.append(path("debug/", debug))\n\n# Add catch-all for React routes\nurlpatterns.append(re_path(r"^(?!api/|admin/|debug/)(?P<path>.*)", serve_frontend))' >> /app/pet_connect_backend/urls.py

# Set simple settings
RUN echo '\n# Simple settings\nDEBUG = True\nALLOWED_HOSTS = ["*"]' >> /app/pet_connect_backend/settings.py

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DEBUG=1

# Create a simple startup script
RUN echo '#!/bin/bash\necho "React files:"\nls -la /app/react_app/\npython manage.py migrate\ngunicorn pet_connect_backend.wsgi:application --bind 0.0.0.0:$PORT' > /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]