"""
Default configuration settings.
"""
import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
                                   

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG') or False
    TESTING = False

    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    CHART_HEIGHT = int(os.environ.get('CHART_HEIGHT', 400))
    REFRESH_INTERVAL = int(os.environ.get('REFRESH_INTERVAL', 30000))
    ENABLE_WEBSOCKET = os.environ.get('ENABLE_WEBSOCKET', 'true').lower() == 'true'
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'false').lower() == 'true'

    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 30))
    API_MAX_RETRIES = int(os.environ.get('API_MAX_RETRIES', 3))
    API_RETRY_BACKOFF_FACTOR = float(os.environ.get('API_RETRY_BACKOFF_FACTOR', 0.5))

    WS_URL = os.environ.get('WS_URL', 'ws://localhost:8000/api/v1/measurements/ws')
    WS_RECONNECT_ATTEMPTS = int(os.environ.get('WS_RECONNECT_ATTEMPTS', 5))
    WS_RECONNECT_DELAY = int(os.environ.get('WS_RECONNECT_DELAY', 3000))

    ENABLE_MOCK_SIMULATOR = os.environ.get('ENABLE_MOCK_SIMULATOR', 'false').lower() == 'true'
    MOCK_RUNNER_URL = os.environ.get('MOCK_RUNNER_URL', 'http://mock-runner:8090')
    MOCK_RUNNER_TOKEN = os.environ.get('MOCK_RUNNER_TOKEN', '')

    DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'
    DEMO_DATA_UPDATE_INTERVAL = int(os.environ.get('DEMO_DATA_UPDATE_INTERVAL', 5000))

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    RATE_LIMIT_DB_PATH = os.environ.get('RATE_LIMIT_DB_PATH', './data/rate-limits.sqlite')
    AUTH_RATE_LIMIT = int(os.environ.get('AUTH_RATE_LIMIT', '10'))
    AUTH_RATE_WINDOW_SECONDS = int(os.environ.get('AUTH_RATE_WINDOW_SECONDS', '300'))
    AI_ANALYSIS_RATE_LIMIT = int(os.environ.get('AI_ANALYSIS_RATE_LIMIT', '5'))
    AI_ANALYSIS_RATE_WINDOW_SECONDS = int(os.environ.get('AI_ANALYSIS_RATE_WINDOW_SECONDS', '3600'))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'

    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-secret-change-in-production'
