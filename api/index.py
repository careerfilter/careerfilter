"""
Vercel Serverless Function Entry Point

This file serves as the entry point for Vercel's Python serverless functions.
It wraps the Django WSGI application for serverless deployment.
"""
import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Get WSGI application
app = get_wsgi_application()

# Vercel handler function
def handler(request, **kwargs):
    """
    Vercel serverless handler function.
    
    This function is called by Vercel for each incoming request.
    It delegates to the Django WSGI application.
    """
    return app(request, **kwargs)

# For Vercel Python runtime compatibility
app = handler

