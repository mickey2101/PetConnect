# pet_connect_backend/pet_connect_backend/test_urls.py
# This is a standalone file to test URL routing

from django.urls import path
from django.http import HttpResponse
from django.views.generic import TemplateView

def test_home(request):
    return HttpResponse("""
    <html>
        <head>
            <title>Pet Connect Test</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #4CAF50; }
                .button { 
                    display: inline-block; 
                    padding: 10px 15px; 
                    background: #4CAF50; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    margin: 10px 0;
                }
            </style>
        </head>
        <body>
            <h1>Pet Connect is working!</h1>
            <p>The Django server is running correctly.</p>
            
            <h2>Test URLs:</h2>
            <ul>
                <li><a href="/api/animals/">API: Animals</a></li>
                <li><a href="/api/users/">API: Users</a></li>
                <li><a href="/api/recommendations/">API: Recommendations</a></li>
                <li><a href="/admin/">Django Admin</a></li>
            </ul>
            
            <p>If you're seeing this page but not your React frontend, it means Django is working but the frontend build isn't being properly served.</p>
        </body>
    </html>
    """)

urlpatterns = [
    path('', test_home),
    path('index.html', test_home),
    # Add the default view for serving React
    path('react/', TemplateView.as_view(template_name='index.html')),
]