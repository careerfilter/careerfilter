"""
App configuration for the jobs app.
"""
from django.apps import AppConfig


class JobsConfig(AppConfig):
    """Configuration for the jobs application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'
    verbose_name = 'Job Board'
    
    def ready(self):
        """Called when the app is ready."""
        # Import signals if needed
        pass
