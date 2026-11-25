"""
Development configuration settings.
"""
from .default import Config


class DevelopmentConfig(Config):
                                    
    DEBUG = True
    DEMO_MODE = True
    ENABLE_CACHING = False
    TEMPLATES_AUTO_RELOAD = True