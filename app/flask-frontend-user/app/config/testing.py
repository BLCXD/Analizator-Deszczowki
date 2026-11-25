"""
Testing configuration settings.
"""
from .default import Config


class TestingConfig(Config):
                                
    TESTING = True
    DEBUG = True
    DEMO_MODE = True
    WTF_CSRF_ENABLED = False