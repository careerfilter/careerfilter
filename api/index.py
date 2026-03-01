# api/index.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# This is the exact name Vercel expects
app = get_wsgi_application()