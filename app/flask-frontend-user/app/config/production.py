"""
Production configuration settings.
"""
import os
from .default import Config


class ProductionConfig(Config):
                                   
    DEBUG = False
    TESTING = False
    DEMO_MODE = False
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'true').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
