"""
Configuration package initialization.
"""
from .default import Config
from .development import DevelopmentConfig
from .testing import TestingConfig
from .production import ProductionConfig

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

__all__ = ['config']