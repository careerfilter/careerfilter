"""
Vercel Serverless Function Entry Point

This file serves as the entry point for Vercel's Python serverless functions.
It wraps the Django WSGI application for serverless deployment.
"""
import os
# import sys
from django.core.wsgi import get_wsgi_application

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = get_wsgi_application()


def handler(request, **kwargs):
    return app(request, **kwargs)
app = handler