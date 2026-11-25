"""
Flask application package initialization.
"""
import os
from .app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))

__all__ = ['app']