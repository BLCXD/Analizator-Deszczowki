# 05_FLASK_FOUNDATION.md
## Inicjalizacja aplikacji, konfiguracja, routing, obsługa błędów i podstawowa struktura projektu

## Cel sekcji
Utworzenie fundamentów aplikacji Flask, w tym inicjalizacji aplikacji, konfiguracji, routingu, obsługi błędów oraz podstawowej struktury projektu zgodnej z wcześniej zaplanowaną architekturą.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie wymagań projektu)
- 02_ARCHITECTURE.md (względem zaplanowanej struktury aplikacji)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (względem konfiguracji i zależności)

Nie ma zależności od innych sekcji implementacyjnych, ale wszystkie kolejne sekcje będą budować na tych fundamentach.

## Stan początkowy
- Katalog `flask-frontend-user` jest pusty
- Utworzono katalog `/sections` z pierwszymi czterema dokumentami
- Brak istniejącej aplikacji Flask
- Zdefiniowano strukturę konfiguracji i zależności w sekcji 04

## Szczegółowy zakres implementacji
### Główna aplikacja Flask (app.py)
Utworzenie głównej aplikacji Flask wykorzystującej wzorzec factory pattern dla lepszej testowalności i konfiguracji.

#### Plik: `/app/app.py`
```python
"""
Main Flask application factory for Analizator Deszczówki Dashboard.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import config

def create_app(config_name=None):
    """
    Application factory pattern implementation.
    
    Args:
        config_name (str): Name of configuration to use (development, testing, production)
        
    Returns:
        Flask: Configured Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/ad_dashboard.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Analizator Deszczówki Dashboard startup')
    
    # Initialize extensions here (when needed)
    # Example: db.init_app(app), login_manager.init_app(app), etc.
    
    # Register blueprints
    from app.controllers.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.controllers.measurements import measurements_bp
    app.register_blueprint(measurements_bp, url_prefix='/measurements')
    
    from app.controllers.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    
    from app.controllers.devices import devices_bp
    app.register_blueprint(devices_bp, url_prefix='/devices')
    
    from app.controllers.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.controllers.settings import settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Shell context for flask cli
    @app.shell_context_processor
    def make_shell_context():
        return {'app': app}
    
    return app


def register_error_handlers(app):
    """Register error handlers for the Flask application."""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f'Bad request: {error}')
        if app.config['ENABLE_CACHING']:
            from flask import make_response, render_template
            return make_response(render_template('errors/400.html'), 400)
        return {'error': 'Bad request'}, 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        app.logger.warning(f'Unauthorized: {error}')
        if app.config['ENABLE_CACHING']:
            from flask import make_response, render_template
            return make_response(render_template('errors/401.html'), 401)
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'Forbidden: {error}')
        if app.config['ENABLE_CACHING']:
            from flask import make_response, render_template
            return make_response(render_template('errors/403.html'), 403)
        return {'error': 'Forbidden'}, 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'Not found: {error}')
        if app.config['ENABLE_CACHING']:
            from flask import make_response, render_template
            return make_response(render_template('errors/404.html'), 404)
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        app.logger.warning(f'Method not allowed: {error}')
        if app.config['ENABLE_CACHING']:
            from flask import make_response, render_template
            return make_response(render_template('errors/405.html'), 405)
        return {'error': 'Method not allowed'}, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server error: {error}')
        if app.config['ENABLE_CACHING']:
            from flask import make_response, render_template
            return make_response(render_template('errors/500.html'), 500)
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(502)
    def bad_gateway_error(error):
        app.logger.error(f'Bad gateway: {error}')
        if app.config['ENABLE_CACHING']:
            from flask import make_response, render_template
            return make_response(render_template('errors/502.html'), 502)
        return {'error': 'Bad gateway'}, 502
    
    @app.errorhandler(503)
    def service_unavailable_error(error):
        app.logger.error(f'Service unavailable: {error}')
        if app.config['ENABLE_CACHING']:
            from flask import make_response, render_template
            return make_response(render_template('errors/503.html'), 503)
        return {'error': 'Service unavailable'}, 503
```

#### Plik: `/app/__init__.py`
```python
"""
Flask application package initialization.
"""
import os
from .app import create_app

# Create the application instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Export the app for use in other modules
__all__ = ['app']
```

#### Plik: `/app/config/__init__.py`
```python
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
```

### Struktura katalogów aplikacji
Utworzenie wszystkich niezbędnych katalogów zgodnie z architekturą z sekcji 02:

#### Katalogi aplikacji
```
flask-frontend-user/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ui_state.py
│   │   └── forms.py
│   │
│   ├── views/
│   │   ├── __init__.py
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   ├── measurements.html
│   │   │   ├── charts.html
│   │   │   ├── devices.html
│   │   │   ├── settings.html
│   │   │   ├── login.html
│   │   │   └── errors/
│   │   │       ├── 400.html
│   │   │       ├── 401.html
│   │   │       ├── 403.html
│   │   │       ├── 404.html
│   │   │       ├── 405.html
│   │   │       └── 500.html
│   │   │
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── header.html
│   │       ├── navbar.html
│   │       ├── footer.html
│   │       ├── metric-card.html
│   │       ├── chart-container.html
│   │       └── status-badge.html
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dashboard.py
│   │   ├── measurements.py
│   │   ├── analytics.py
│   │   ├── devices.py
│   │   ├── auth.py
│   │   └── settings.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── websocket_service.py
│   │   ├── auth_service.py
│   │   └── data_processor.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   ├── responsive.css
│   │   │   ├── components.css
│   │   │   └── animations.css
│   │   │
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── api.js
│   │   │   ├── websocket.js
│   │   │   ├── charts.js
│   │   │   ├── ui.js
│   │   │   └── utils.js
│   │   │
│   │   └── vendor/
│   │       ├── anime.js
│   │       ├── chart.js
│   │       └── README.md  # Information about vendor files
│   │
│   └── config/
│       ├── __init__.py
│       ├── default.py
│       ├── development.py
│       ├── testing.py
│       └── production.py
│
├── migrations/
├── tests/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
│
├── docs/
├── requirements.txt
├── config.py
├── wsgi.py
├── Dockerfile
└── README.md
```

### Pliki konfiguracyjne
#### Plik: `/app/config/default.py`
```python
"""
Default configuration settings.
"""
import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG') or False
    TESTING = False
    
    # Application settings
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    CHART_HEIGHT = int(os.environ.get('CHART_HEIGHT', 400))
    REFRESH_INTERVAL = int(os.environ.get('REFRESH_INTERVAL', 30000))
    ENABLE_WEBSOCKET = os.environ.get('ENABLE_WEBSOCKET', 'true').lower() == 'true'
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'false').lower() == 'true'
    
    # Backend API configuration
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 30))
    API_MAX_RETRIES = int(os.environ.get('API_MAX_RETRIES', 3))
    API_RETRY_BACKOFF_FACTOR = float(os.environ.get('API_RETRY_BACKOFF_FACTOR', 0.5))
    
    # WebSocket configuration
    WS_URL = os.environ.get('WS_URL', 'ws://localhost:8000/ws')
    WS_RECONNECT_ATTEMPTS = int(os.environ.get('WS_RECONNECT_ATTEMPTS', 5))
    WS_RECONNECT_DELAY = int(os.environ.get('WS_RECONNECT_DELAY', 3000))
    
    # Demo mode
    DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'
    DEMO_DATA_UPDATE_INTERVAL = int(os.environ.get('DEMO_DATA_UPDATE_INTERVAL', 5000))
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-secret-change-in-production'
```

#### Plik: `/app/config/development.py`
```python
"""
Development configuration settings.
"""
from .default import Config


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DEMO_MODE = True  # Enable demo mode by default in development
    # Disable caching in development to see changes immediately
    ENABLE_CACHING = False
    # Enable template auto-reloading
    TEMPLATES_AUTO_RELOAD = True
```

#### Plik: `/app/config/testing.py`
```python
"""
Testing configuration settings.
"""
from .default import Config


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    # Use in-memory database or mock services for testing
    DEMO_MODE = True
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
```

#### Plik: `/app/config/production.py`
```python
"""
Production configuration settings.
"""
from .default import Config


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # In production, rely on environment variables for sensitive data
    # Caching can be enabled for performance
    # Demo mode should be disabled in production
    DEMO_MODE = False
    # Enable caching for better performance
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'true').lower() == 'true'
    # Use a proper secret key in production (must be set via environment variable)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")
```

### Bazowy kontroler
#### Plik: `/app/controllers/base.py`
```python
"""
Base controller class with common functionality.
"""
from flask import Blueprint, render_template, current_app, request, session, jsonify
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def create_blueprint(name, import_name, url_prefix=None):
    """
    Factory function to create a blueprint with common setup.
    
    Args:
        name (str): Name of the blueprint
        import_name (str): Import name for the blueprint
        url_prefix (str): URL prefix for all routes in this blueprint
        
    Returns:
        Blueprint: Configured Flask blueprint
    """
    bp = Blueprint(name, import_name, url_prefix=url_prefix)
    
    # Add common template context processors
    @bp.app_context_processor
    def inject_common_vars():
        return {
            'app_name': 'Analizator Deszczówki',
            'app_version': '0.1.0',
            'current_year': 2026
        }
    
    return bp


def login_required(f):
    """
    Decorator to require authentication for a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simple authentication check - to be implemented based on actual auth mechanism
        if not session.get('authenticated'):
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def api_key_required(f):
    """
    Decorator to require API key for a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config.get('API_KEY'):
            if request.is_json:
                return jsonify({'error': 'Valid API key required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def handle_api_errors(f):
    """
    Decorator to handle API errors consistently.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {f.__name__}: {str(e)}", exc_info=True)
            if request.is_json:
                return jsonify({'error': 'Internal server error'}), 500
            # For HTML responses, we'll let Flask's error handlers deal with it
            raise
    return decorated_function
```

### Szablon podstawowy
#### Plik: `/app/views/templates/base.html`
```html
<!DOCTYPE html>
<html lang="pl" class="theme-dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Analizator Deszczówki{% endblock %}</title>
    
    <!-- Favicon -->
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
    
    <!-- CSS Styles -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/animations.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/responsive.css') }}">
    
    <!-- HTML5 Shiv and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
    <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
    <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
    
    {% block extra_head %}{% endblock %}
</head>
<body>
    <!-- Preloader for initial load -->
    <div id="preloader">
        <div class="spinner"></div>
    </div>
    
    <!-- Main container -->
    <div id="app">
        <!-- Header -->
        <header class="app-header">
            {% include 'components/header.html' %}
        </header>
        
        <!-- Sidebar (hidden on mobile) -->
        <aside class="app-sidebar">
            {% include 'components/navbar.html' %}
        </aside>
        
        <!-- Main content -->
        <main class="app-main">
            <div class="app-content">
                {% block content %}{% endblock %}
            </div>
        </main>
        
        <!-- Footer -->
        <footer class="app-footer">
            {% include 'components/footer.html' %}
        </footer>
    </div>
    
    <!-- JavaScript -->
    <script src="{{ url_for('static', filename='js/utils.js') }}"></script>
    <script src="{{ url_for('static', filename='js/ui.js') }}"></script>
    <script src="{{ url_for('static', filename='js/api.js') }}"></script>
    <script src="{{ url_for('static', filename='js/websocket.js') }}"></script>
    <script src="{{ url_for('static', filename='js/charts.js') }}"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    
    {% block extra_js %}{% endblock %}
    
    <!-- Vendor libraries -->
    <script src="{{ url_for('static', filename='vendor/anime.js') }}"></script>
    <script src="{{ url_for('static', filename='vendor/chart.js') }}"></script>
</body>
</html>
```

#### Plik: `/app/views/templates/index.html` (dashboard overview)
```html
{% extends "base.html" %}

{% block title %}Analizator Deszczówki - Dashboard{% endblock %}

{% block extra_head %}
<meta name="description" content="Główny dashboard analizatora deszczówki pokazujący aktualne pomiary i stan systemu">
{% endblock %}

{% block content %}
<div class="dashboard-grid">
    <!-- System Status -->
    <div class="dashboard-card wide">
        <div class="card-header">
            <h2>Stan Systemu</h2>
            <div class="card-actions">
                <button class="btn btn-sm btn-outline" id="refresh-system-btn">
                    <i class="refresh-icon"></i> Odśwież
                </button>
            </div>
        </div>
        <div class="card-body" id="system-status-container">
            <!-- System status will be loaded here via JavaScript -->
            <div class="loading-placeholder">Ładowanie stanu systemu...</div>
        </div>
    </div>
    
    <!-- Current Measurements -->
    <div class="dashboard-card wide">
        <div class="card-header">
            <h2>Aktualne Pomiarów</h2>
            <div class="card-actions">
                <button class="btn btn-sm btn-outline" id="refresh-measurements-btn">
                    <i class="refresh-icon"></i> Odśwież
                </button>
            </div>
        </div>
        <div class="card-body" id="current-measurements-container">
            <!-- Current measurements will be loaded here via JavaScript -->
            <div class="loading-placeholder">Ładowanie aktualnych pomiarów...</div>
        </div>
    </div>
    
    <!-- Quick Stats -->
    <div class="dashboard-card medium">
        <div class="card-header">
            <h2>Szybkie Statystyki</h2>
        </div>
        <div class="card-body" id="quick-stats-container">
            <!-- Quick stats will be loaded here via JavaScript -->
            <div class="loading-placeholder">Ładowanie statystyk...</div>
        </div>
    </div>
    
    <!-- Recent Activity -->
    <div class="dashboard-card wide">
        <div class="card-header">
            <h2>Ostatnia Aktywność</h2>
        </div>
        <div class="card-body" id="recent-activity-container">
            <!-- Recent activity will be loaded here via JavaScript -->
            <div class="loading-placeholder">Ładowanie ostatniej aktywności...</div>
        </div>
    </div>
    
    <!-- Alerts & Notifications -->
    <div class="dashboard-card wide">
        <div class="card-header">
            <h2>Powiadomienia</h2>
            <div class="card-actions">
                <button class="btn btn-sm btn-outline" id="clear-notifications-btn">
                    <i class="clear-icon"></i> Wyczyść
                </button>
            </div>
        </div>
        <div class="card-body" id="notifications-container">
            <!-- Notifications will be loaded here via JavaScript -->
            <div class="loading-placeholder">Ładowanie powiadomień...</div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
{% endblock %}
```

### Inicjalizacja bazy danych (jeśli będzie potrzebna lokalnie)
#### Plik: `/migrations/env.py` (placeholder - tylko jeśli potrzebne lokalne migracje)
```python
"""
Alembic migration environment.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_main_option("sqlalchemy.url"),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Plik wsgi.py dla wdrożenia
#### Plik: `/wsgi.py`
```python
"""
WSGI entry point for deployment.
"""
from app import create_app
import os

application = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    application.run()
```

### Plik Dockerfile (opcjonalnie)
#### Plik: `/Dockerfile`
```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"]
```

### Plik requirements.txt
#### Plik: `/requirements.txt`
```txt
Flask>=2.0.0
Flask-WTF>=1.0.0
Flask-Login>=0.5.0
requests>=2.25.0
python-socketio>=5.0.0
python-dateutil>=2.8.0
python-dotenv>=0.15.0
pytest>=6.0.0
pytest-cov>=2.10.0
Flask-Testing>=0.8.0
black>=21.0.0
flake8>=3.8.0
pre-commit>=2.10.0
gunicorn>=20.0.0  # For production deployment
```

### Plik .env.example
#### Plik: `/.env.example`
```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1

# Secret Key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-super-secret-key-here-change-in-production

# Backend API Configuration
API_BASE_URL=http://localhost:8000
API_VERSION=v1
API_TIMEOUT=30
API_MAX_RETRIES=3
API_RETRY_BACKOFF_FACTOR=0.5

# WebSocket Configuration
WS_URL=ws://localhost:8000/ws
WS_RECONNECT_ATTEMPTS=5
WS_RECONNECT_DELAY=3000

# Application Settings
ITEMS_PER_PAGE=20
CHART_HEIGHT=400
REFRESH_INTERVAL=30000
ENABLE_WEBSOCKET=true
ENABLE_CACHING=false

# Demo Mode
DEMO_MODE=false
DEMO_DATA_UPDATE_INTERVAL=5000
```

### Test podstawowej aplikacji
#### Plik: `/tests/unit/test_app.py`
```python
"""
Unit tests for the Flask application factory.
"""
import pytest
from app import create_app
from config import TestingConfig


def test_app_creation():
    """Test that the application factory creates a valid Flask app."""
    app = create_app('testing')
    assert app is not None
    assert app.config['TESTING'] is True


def test_app_config():
    """Test that the application uses the correct configuration."""
    app = create_app('testing')
    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is True
    assert app.config['SECRET_KEY'] == 'dev-key-change-in-production'


def test_blueprints_registered():
    """Test that all expected blueprints are registered."""
    app = create_app('testing')
    # Get all registered blueprint names
    blueprint_names = [bp.name for bp in app.blueprints.values()]
    
    # Check for expected blueprints
    expected_blueprints = [
        'dashboard',
        'measurements',
        'analytics',
        'devices',
        'auth',
        'settings'
    ]
    
    for blueprint in expected_blueprints:
        assert blueprint in blueprint_names, f"Blueprint '{blueprint}' not registered"


def test_error_handlers():
    """Test that error handlers are registered."""
    app = create_app('testing')
    # Test 404 handler
    with app.test_client() as client:
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        # Check that we get JSON response (since we're not using templates in test)
        assert b'Not found' in response.data or b'error' in response.data
```

### Instrukcje uruchamiania
#### Dodatek do README.md (do utworzenia w późniejszej sekcji)
```
## Uruchomienie aplikacji

### Wymagania wstępne
- Python 3.8+
- Dostęp do backend API Analizatora Deszczówki (działający na localhost:8000 lub innym skonfigurowanym URL)

### Instalacja
1. Sklonuj repozytorium
2. Utwórz środowisko wirtualne:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```
4. Skonfiguruj zmienne środowiskowe:
   ```bash
   cp .env.example .env
   # Edytuj .env i ustaw odpowiednie wartości
   ```

### Uruchomienie w trybie development
```bash
flask run
# lub
python -m flask run
```

### Uruchomienie w trybie production
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:application
```

### Uruchomienie testów
```bash
# Unit tests
pytest tests/unit/

# All tests
pytest tests/

# With coverage
pytest --cov=app tests/
```
```

### Pliki, które należy utworzyć lub zmodyfikowane
W ramach tej sekcji zostaną utworzone następujące pliki:

**Główna aplikacja:**
- `/app/app.py` - główna aplikacja Flask z factory pattern
- `/app/__init__.py` - inicjalizacja pakietu aplikacji

**Konfiguracja:**
- `/app/config/__init__.py` - pakiet konfiguracji
- `/app/config/default.py` - domyślna konfiguracja
- `/app/config/development.py` - konfiguracja rozwojowa
- `/app/config/testing.py` - konfiguracja testowa
- `/app/config/production.py` - konfiguracja produkcyjna

**Kontrolery:**
- `/app/controllers/__init__.py` - pakiet kontrolerów
- `/app/controllers/base.py` - bazowy kontroler z wspólną funkcjonalnością

**Szablony:**
- `/app/views/templates/base.html` - bazowy szablon HTML
- `/app/views/templates/index.html` - strona główna/dashboard
- Szablony błędów (do utworzenia w sekcji 14)

**Komponenty:**
- `/app/views/components/__init__.py` - pakiet komponentów
- `/app/views/components/header.html` - komponent nagłówka
- `/app/views/components/navbar.html` - komponent nawigacji
- `/app/views/components/footer.html` - komponent stopki
- `/app/views/components/metric-card.html` - komponent karty metrycznej
- `/app/views/components/chart-container.html` - komponent kontenera wykresu
- `/app/views/components/status-badge.html` - komponent wskaźnika statusu

**Statyczne pliki:**
- `/app/static/css/main.css` - główne style CSS
- `/app/static/css/components.css` - style dla komponentów
- `/app/static/css/animations.css` - style dla animacji
- `/app/static/css/responsive.css` - style responsywne
- `/app/static/js/main.js` - główny plik JavaScript
- `/app/static/js/utils.js` - funkcje pomocnicze
- `/app/static/js/ui.js` - funkcje interfejsu użytkownika
- `/app/static/js/api.js` - funkcje komunikacji z API
- `/app/static/js/websocket.js` - obsługa WebSocket
- `/app/static/js/charts.js` - obsługa wykresów
- `/app/static/vendor/anime.js` - biblioteka animacji
- `/app/static/vendor/chart.js` - biblioteka wykresów

**Pliki konfiguracyjne projektu:**
- `/requirements.txt` - lista zależności Python
- `/.env.example` - przykładowy plik zmiennych środowiskowych
- `/wsgi.py` - punkt wejścia WSGI
- `/Dockerfile` - instrukcje konteneryzacji (opcjonalnie)

**Testy:**
- `/tests/unit/test_app.py` - podstawowe testy aplikacji

### Integracja z pozostałymi elementami systemu
Fundamenty aplikacji zapewniają:
- Solidną podstawę dla wszystkich kolejnych funkcjonalności dashboardu
- Modułową strukturę umożliwiającą łatwe dodawanie nowych funkcji
- Oddzielenie odpowiedzialności między różnymi warstwami aplikacji
- Konfigurowalność dla różnych środowisk (development, testing, production)
- Obsługę błędów i logowanie
- Gotowość do wdrożenia poprzez WSGI i Docker
- Testowalność poprzez factory pattern i modularną strukturę
- Zgodność z wcześniej zaplanowaną architekturą i systemem projektowym

### Obsługa błędów i przypadków brzegowych
Fundamenty zawierają mechanizmy radzenia sobie z różnymi sytuacjami:

#### Błędy aplikacji
- **Błędy 4xx**: obsługa błędów klienta (złe żądanie, nieautoryzowany dostęp, zakaz, nie znaleziono, niedozwolona metoda)
- **Błędy 5xx**: obsługa błędów serwera (wewnętrzny błąd serwera, zła bramka, niedostępna usługa)
- **Błędy obsługi szablonów**: fallback na odpowiedzi JSON gdy szablony nie są dostępne lub wyłączone
- **Błędy konfiguracji**: wyraźne komunikaty gdy brakuje wymaganych zmiennych środowiskowych

#### Błędy połączenia
- **Timeout**: mechanizm ponawiania żądań z wykładniczym opóźnieniem w kliencie API
- **Błędy połączenia**: obsługa błędów połączenia z backendem
- **Nieprawidłowe odpowiedzi**: walidacja formatu JSON i struktury danych z odpowiednimi komunikatami o błędach

#### Błędy środowiskowe
- **Brak zależności**: wyraźne komunikaty podczas uruchamiania aplikacji
- **Niezgodne wersje Python**: wymuszenie minimalnej wersji poprzez zależności
- **Problemy z uprawnieniami**: obsługa błędów systemowych podczas dostępu do zasobów

#### Przypadki brzegowe
- **Puste żądania**: obsługa żądań bez treści lub z nieprawidłową treścią
- **Duże żądania**: ograniczenie rozmiaru żądań w konfiguracji serwera WSGI
- **Jednoczesne żądania**: wykorzystanie produkcyjnego serwera WSGI (Gunicorn) do obsługi wielu żądań
- **Sesje wygasłe**: mechanizm wykrywania i przekierowywania do logowania
- **Wygaśnięcie tokenów**: przygotowanie do odświeżania tokenów dostępu

### Testy wymagane do uznania sekcji za ukończoną
- Uruchomienie aplikacji bez błędów w trybie development
- Rejestracja wszystkich zaplanowanych blueprintów (kontrolerów)
- Prawidłowe ładowanie szablonu podstawowego i stron dziedziczących
- Rejestracja obsługi błędów dla wszystkich standardowych kodów HTTP
- Skonfigurowanie logowania aplikacji
- Pomyślne uruchomienie podstawowych testów jednostkowych
- Weryfikacja, że aplikacja używa prawidłowej konfiguracji dla danego środowiska
- Sprawdzenie, że wszystkie wymagane pliki i katalogi zostały utworzone zgodnie z architekturą

### Jednoznaczne kryteria akceptacji
- Dokument zawiera kompletną implementację głównej aplikacji Flask z factory pattern
- Zdefiniowano strukturę konfiguracji wspierającą różne środowiska
- Utworzono wszystkie niezbędne katalogi i pliki zgodnie z zaplanowaną architekturą
- Zaimplementowano bazowy kontroler z wspólną funkcjonalnością
- Utworzono bazowy szablon HTML i stronę główną/dashboard
- Dokumentowano mechanizmy obsługi błędów i logowania
- Przygotowano pliki konfiguracyjne projektu (requirements.txt, .env.example)
- Utworzono podstawowe testy jednostkowe dla aplikacji
- Wszystkie elementy są zgodne z wcześniej zaplanowaną architekturą i systemem projektowym

### Zależności od innych sekcji
- Wymaga ukończenia: 01_PROJECT_ANALYSIS.md, 02_ARCHITECTURE.md, 04_ENVIRONMENT_AND_CONFIGURATION.md
- Jest wymaganiem wstępnym dla: wszystkie sekcje implementacyjne (06-20)

### Warunki zakończenia prac
Uznać sekcję za zakończoną gdy:
- Utworzono kompletną aplikację Flask z factory pattern
- Zdefiniowano strukturę konfiguracji dla różnych środowisk
- Utworzono wszystkie niezbędne katalogi zgodnie z architekturą aplikacji
- Zaimplementowano bazowy kontroler i podstawowe szablony
- Dokumentowano mechanizmy obsługi błędów i logowania
- Przygotowano pliki konfiguracyjne projektu
- Utworzono podstawowe testy jednostkowe
- Weryfikowano, że aplikacja może być uruchomiona bez błędów

### Informacje, które należy przekazać do kolejnych sekcji
- Struktura aplikacji i sposób rejestracji blueprintów
- Interfejs bazowego kontrolera i dekoratorów
- Szablon podstawowy i sposób dziedziczenia szablonów
- Lokalizacja i struktura plików statycznych (CSS, JavaScript)
- Mechanizm obsługi błędów i logowania
- Konfiguracja aplikacji dla różnych środowisk
- Instrukcje dotyczące uruchamiania aplikacji w trybie development i production
- Podejście do testowania aplikacji
