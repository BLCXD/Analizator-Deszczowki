# 04_ENVIRONMENT_AND_CONFIGURATION.md
## Środowisko Python, zależności, zmienne środowiskowe, konfiguracja Flaska i połączenie z backendem

## Cel sekcji
Zdefiniowanie środowiska uruchomieniowego, zależności, konfiguracji aplikacji Flask oraz sposobu połączenia z istniejącym backendem API Analizatora Deszczówki.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie rzeczywistego backendu i jego wymagań)
- 02_ARCHITECTURE.md (względem struktury aplikacji, gdzie będzie umieszczona konfiguracja)

Nie ma zależności od innych sekcji konfiguracyjnych, ale wszystkie kolejne sekcje implementacyjne będą zależały od prawidłowo skonfigurowanego środowiska.

## Stan początkowy
- Katalog `flask-frontend-user` jest pusty
- Brak istniejącego pliku requirements.txt lub konfiguracji
- Brak zdefiniowanych zmiennych środowiskowych
- Backend jest dostępny i udostępnia dokumentowane endpointy (z analizy w sekcji 01)

## Szczegółowy zakres implementacji
### Środowisko Python i zależności
Aplikacja Flask będzie wymagała określonego środowiska Python oraz zależności do prawidłowego funkcjonowania.

#### Wersja Python
- **Wymagana wersja**: Python 3.8+
- **Zalecana wersja**: Python 3.10 lub 3.11 dla lepszej wydajności i bezpieczeństwa
- **Uzasadnienie**: Nowsze wersje Pythona zapewniają lepszą wydajność, poprawki bezpieczeństwa oraz dostęp do nowszych funkcji języka

#### Virtual Environment
- **Zalecane narzędzie**: `venv` (wbudowane w Python 3.3+) lub `virtualenv`
- **Ścieżka środowiska**: `venv/` w katalogu projektu
- **Aktywacja**:
  - Linux/macOS: `source venv/bin/activate`
  - Windows: `venv\Scripts\activate`

#### Główne zależności (requirements.txt)
Aplikacja będzie wymagała następujących pakietów Python:

1. **Framework webowy**
   - `Flask>=2.0.0` - podstawowy framework
   - `Flask-WTF>=1.0.0` - obsługa formularzy i walidacji (opcjonalnie, można użyć własnej implementacji)
   - `Flask-Login>=0.5.0` - zarządzanie sesjami użytkowników (jeśli wymagane uwierzytelnianie)

2. **Komunikacja z backendem**
   - `requests>=2.25.0` - biblioteka HTTP do komunikacji z REST API
   - `python-socketio>=5.0.0` - klient WebSocket (jeśli backend obsługuje streaming przez WebSocket)
   - lub `websocket-client>=1.0.0` - prostszy klient WebSocket

3. **Przetwarzanie danych**
   - `python-dateutil>=2.8.0` - obsługa dat i czasów
   - `Pandas>=1.3.0` (opcjonalnie) - do zaawansowanego przetwarzania i analizy danych
   - lub wbudowane moduły `datetime`, `json` dla prostszych operacji

4. **Środowisko i konfiguracja**
   - `python-dotenv>=0.15.0` - ładowanie zmiennych środowiskowych z pliku .env
   - `Marshmallow>=3.0.0` (opcjonalnie) - walidacja danych lub można użyć wbudowanych mechanizmów Flask

5. **Jakość kodu i testowanie**
   - `pytest>=6.0.0` - framework testowy
   - `pytest-cov>=2.10.0` - pokrycie kodu testami
   - `Flask-Testing>=0.8.0` (opcjonalnie) - narzędzia do testowania aplikacji Flask
   - `black>=21.0.0` - formatowanie kodu
   - `flake8>=3.8.0` - linternik
   - `pre-commit>=2.10.0` - zarządzanie hookami przed commit

#### Przykładowy plik requirements.txt
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
```

### Zmienne środowiskowe
Aplikacja będzie wykorzystywała zmienne środowiskowe do konfiguracji różnych aspektów działania, zgodnie z zasadą 12-factor app.

#### Wymagane zmienne środowiskowe
1. **Konfiguracja aplikacji**
   - `FLASK_APP=app.py` - punkt wejścia aplikacji Flask
   - `FLASK_ENV=development` lub `production` - środowisko uruchomieniowe
   - `FLASK_DEBUG=0` lub `1` - tryb debugowania (wyłączony w produkcji)

2. **Klucz tajny**
   - `SECRET_KEY=` - klucz tajny do签名 sesji i tokenów CSRF (wymagany, musi być długi i losowy)

3. **Konfiguracja backendu**
   - `API_BASE_URL=` - podstawowy URL backend API (np. `http://localhost:8000` lub `https://api.example.com`)
   - `API_VERSION=v1` - wersja API (domyślnie v1 według analizy backendu)
   - `API_TIMEOUT=30` - timeout dla żądań HTTP w sekundach
   - `API_MAX_RETRIES=3` - maksymalna liczba prób ponowienia żądań
   - `API_RETRY_BACKOFF_FACTOR=0.5` - czynnik wykładniczego opóźnienia między próbami

4. **WebSocket (jeśli używane)**
   - `WS_URL=` - URL WebSocket backendu (np. `ws://localhost:8000/ws`)
   - `WS_RECONNECT_ATTEMPTS=5` - liczba prób ponownego połączenia WebSocket
   - `WS_RECONNECT_DELAY=3000` - opóźnienie między próbami ponownego połączenia w ms

5. **Uwierzytelnianie (jeśli wymagane przez backend)**
   - `DEFAULT_DEVICE_ID=` - domyślne ID urządzenia do użycia podczas developmentu
   - `DEFAULT_DEVICE_SECRET=` - domyślny sekret urządzenia (tylko dla developmentu!)
   - `TOKEN_REFRESH_THRESHOLD=300` - sekundy przed wygaśnięciem tokenu, kiedy go odświeżać

6. **Konfiguracja aplikacji**
   - `ITEMS_PER_PAGE=20` - liczba elementów na stronę w paginacji
   - `CHART_HEIGHT=400` - domyślna wysokość wykresów w pikselach
   - `REFRESH_INTERVAL=30000` - interwał odświeżania danych w ms (5 minut)
   - `ENABLE_WEBSOCKET=true` - czy używać WebSocket do streamingu danych
   - `ENABLE_CACHING=false` - czy włączyć prosty cache odpowiedzi API (w rozwoju zwykle wyłączony)

7. **Tryb demonstracyjny (opcjonalnie)**
   - `DEMO_MODE=false` - czy włączyć tryb demonstracyjny z symulowanymi danymi
   - `DEMO_DATA_UPDATE_INTERVAL=5000` - interwał aktualizacji danych demonstracyjnych w ms

#### Przykładowy plik .env
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

# Authentication (Development Only!)
DEFAULT_DEVICE_ID=test-device-001
DEFAULT_DEVICE_SECRET=test-secret-123

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

#### Przykładowy plik .env.example
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

### Konfiguracja Flaska
Aplikacja Flask będzie miała modularną konfigurację wspierającą różne środowiska (development, testing, production).

#### Struktura konfiguracji
```
flask-frontend-user/
├── config/
│   ├── __init__.py
│   ├── default.py        # Domyślna konfiguracja
│   ├── development.py    # Konfiguracja rozwojowa
│   ├── testing.py        # Konfiguracja testowa
│   └── production.py     # Konfiguracja produkcyjna
└── app.py                # Główna aplikacja Flask
```

#### Plik config/__init__.py
```python
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


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DEMO_MODE = True  # Enable demo mode by default in development
    # Disable caching in development to see changes immediately
    ENABLE_CACHING = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    # Use in-memory database or mock services for testing
    DEMO_MODE = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # In production, rely on environment variables for sensitive data
    # Caching can be enabled for performance
    # Demo mode should be disabled in production
    DEMO_MODE = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

#### Integracja konfiguracji z aplikacją (app.py)
```python
from flask import Flask
from config import config
import os

def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions here
    # db.init_app(app)
    # login_manager.init_app(app)
    # csrf.init_app(app)
    
    # Register blueprints
    from app.controllers.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.controllers.measurements import measurements_bp
    app.register_blueprint(measurements_bp, url_prefix='/measurements')
    
    # ... other blueprints
    
    return app
```

### Połączenie z backendem API
Implementacja warstwy usług odpowiedzialnej za komunikację z backendem API Analizatora Deszczówki.

#### Klient API (services/api_client.py)
```python
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import json
from threading import Lock
import time

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with the AD backend API."""
    
    def __init__(self, base_url: str, api_version: str = 'v1', 
                 timeout: int = 30, max_retries: int = 3,
                 backoff_factor: float = 0.5):
        self.base_url = base_url.rstrip('/')
        self.api_version = api_version
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = requests.Session()
        self._token = None
        self._token_expiry = None
        self._token_lock = Lock()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for API endpoint."""
        return urljoin(f"{self.base_url}/api/{self.api_version}/", endpoint.lstrip('/'))
    
    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate exceptions."""
        try:
            response.raise_for_status()
            if response.content:
                return response.json()
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise ValueError("Invalid JSON response from API")
    
    def _request_with_retry(self, method: str, url: str, **kwargs) -> Any:
        """Make HTTP request with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method, url, 
                    timeout=self.timeout,
                    **kwargs
                )
                return self._handle_response(response)
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout) as e:
                last_exception = e
                if attempt < self.max_retries:
                    # Exponential backoff
                    sleep_time = self.backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {sleep_time:.1f}s..."
                    )
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Request failed after {self.max_retries + 1} attempts: {e}")
            except requests.exceptions.HTTPError as e:
                # Don't retry on HTTP errors (4xx, 5xx) except for specific cases
                if e.response.status_code in [429, 500, 502, 503, 504]:
                    last_exception = e
                    if attempt < self.max_retries:
                        sleep_time = self.backoff_factor * (2 ** attempt)
                        logger.warning(
                            f"HTTP error {e.response.status_code} (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                            f"Retrying in {sleep_time:.1f}s..."
                        )
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"HTTP error after {self.max_retries + 1} attempts: {e}")
                else:
                    # Client errors (4xx) or other server errors - don't retry
                    raise
        
        # If we got here, all retries failed
        raise last_exception
    
    def set_auth_token(self, token: str, expires_in: int = 1800):
        """Set authentication token for API requests."""
        with self._token_lock:
            self._token = token
            self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def clear_auth_token(self):
        """Clear authentication token."""
        with self._token_lock:
            self._token = None
            self._token_expiry = None
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
    
    def is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        with self._token_lock:
            return self._token is not None and \
                   self._token_expiry is not None and \
                   datetime.now() < self._token_expiry
    
    # Measurement API methods
    def create_measurement(self, measurement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new measurement."""
        url = self._build_url('measurements/')
        return self._request_with_retry('POST', url, json=measurement_data)
    
    def get_measurements(self, device_id: Optional[str] = None, 
                         skip: int = 0, limit: int = 100,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get measurements with optional filtering."""
        params = {
            'skip': skip,
            'limit': limit
        }
        if device_id:
            params['device_id'] = device_id
        if start_time:
            params['start_time'] = start_time.isoformat()
        if end_time:
            params['end_time'] = end_time.isoformat()
            
        url = self._build_url('measurements/')
        return self._request_with_retry('GET', url, params=params)
    
    def get_latest_measurement(self, device_id: str) -> Dict[str, Any]:
        """Get the latest measurement for a device."""
        url = self._build_url(f'measurements/{device_id}/latest')
        return self._request_with_retry('GET', url)
    
    def get_measurements_by_device(self, device_id: str, 
                                   skip: int = 0, limit: int = 100,
                                   start_time: Optional[datetime] = None,
                                   end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get measurements for a specific device."""
        params = {
            'skip': skip,
            'limit': limit
        }
        if start_time:
            params['start_time'] = start_time.isoformat()
        if end_time:
            params['end_time'] = end_time.isoformat()
            
        url = self._build_url(f'measurements/{device_id}')
        return self._request_with_retry('GET', url, params=params)
    
    def get_measurement_trends(self, device_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get measurement trends for a device."""
        url = self._build_url(f'measurements/{device_id}/analysis/trends')
        params = {'hours': hours}
        return self._request_with_retry('GET', url, params=params)
    
    def get_measurement_anomalies(self, device_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get measurement anomalies for a device."""
        url = self._build_url(f'measurements/{device_id}/analysis/anomalies')
        params = {'hours': hours}
        return self._request_with_retry('GET', url, params=params)
    
    # Device API methods
    def get_devices(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of devices."""
        params = {'skip': skip, 'limit': limit}
        url = self._build_url('devices/')
        return self._request_with_retry('GET', url, params=params)
    
    def get_device(self, device_id: str) -> Dict[str, Any]:
        """Get a specific device."""
        url = self._build_url(f'devices/{device_id}')
        return self._request_with_retry('GET', url)
    
    # Health check
    def health_check(self) -> Dict[str, Any]:
        """Check backend health."""
        url = urljoin(self.base_url, '/health')
        return self._request_with_retry('GET', url)
    
    def close(self):
        """Close the session."""
        self.session.close()
```

#### WebSocket Service (services/websocket_service.py)
```python
import socketio
import logging
from typing import Callable, Optional
import json
from threading import Thread, Event
import time

logger = logging.getLogger(__name__)


class WebSocketService:
    """Service for handling WebSocket connection to AD backend."""
    
    def __init__(self, url: str, reconnect_attempts: int = 5, 
                 reconnect_delay: int = 3000):
        self.url = url
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay / 1000.0  # Convert to seconds
        self.sio = socketio.Client(reconnection_attempts=0)  # We handle reconnection manually
        self.connected = False
        self._reconnect_thread: Optional[Thread] = None
        self._stop_event = Event()
        self._message_handlers: Dict[str, List[Callable]] = {}
        self._connect_handlers: List[Callable] = []
        self._disconnect_handlers: List[Callable] = []
        
        # Set up SocketIO event handlers
        self._setup_socketio_handlers()
    
    def _setup_socketio_handlers(self):
        """Set up default SocketIO event handlers."""
        @self.sio.event
        def connect():
            logger.info("WebSocket connected")
            self.connected = True
            self._stop_event.clear()
            for handler in self._connect_handlers:
                try:
                    handler()
                except Exception as e:
                    logger.error(f"Error in connect handler: {e}")
        
        @self.sio.event
        def disconnect():
            logger.info("WebSocket disconnected")
            self.connected = False
            for handler in self._disconnect_handlers:
                try:
                    handler()
                except Exception as e:
                    logger.error(f"Error in disconnect handler: {e}")
            
            # Attempt reconnection if not stopping
            if not self._stop_event.is_set():
                self._schedule_reconnect()
        
        @self.sio.event
        def connect_error(data):
            logger.error(f"WebSocket connection error: {data}")
            self.connected = False
    
    def _schedule_reconnect(self):
        """Schedule a reconnection attempt."""
        if self._reconnect_thread and self._reconnect_thread.is_alive():
            return  # Already reconnecting
            
        self._reconnect_thread = Thread(target=self._reconnect_loop)
        self._reconnect_thread.daemon = True
        self._reconnect_thread.start()
    
    def _reconnect_loop(self):
        """Loop to handle reconnection attempts."""
        attempt = 0
        while attempt < self.reconnect_attempts and not self._stop_event.is_set():
            try:
                logger.info(f"Attempting to reconnect WebSocket (attempt {attempt + 1}/{self.reconnect_attempts})")
                self.sio.connect(self.url, wait_timeout=10)
                if self.connected:
                    logger.info("WebSocket reconnected successfully")
                    return
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt + 1} failed: {e}")
            
            attempt += 1
            if attempt < self.reconnect_attempts and not self._stop_event.is_set():
                logger.info(f"Waiting {self.reconnect_delay}s before next reconnection attempt")
                self._stop_event.wait(self.reconnect_delay)
        
        if not self.connected and not self._stop_event.is_set():
            logger.error(f"Failed to reconnect WebSocket after {self.reconnect_attempts} attempts")
    
    def on(self, event: str, handler: Callable):
        """Register a handler for a specific event."""
        if event not in self._message_handlers:
            self._message_handlers[event] = []
        self._message_handlers[event].append(handler)
        
        # Register with SocketIO
        @self.sio.on(event)
        def handle_event(data):
            logger.debug(f"Received WebSocket event '{event}': {data}")
            for handler in self._message_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in WebSocket event handler for '{event}': {e}")
    
    def on_connect(self, handler: Callable):
        """Register a handler for connection events."""
        self._connect_handlers.append(handler)
    
    def on_disconnect(self, handler: Callable):
        """Register a handler for disconnection events."""
        self._disconnect_handlers.append(handler)
    
    def emit(self, event: str, data: Any):
        """Emit an event to the WebSocket server."""
        if self.connected:
            try:
                self.sio.emit(event, data)
            except Exception as e:
                logger.error(f"Error emitting WebSocket event '{event}': {e}")
        else:
            logger.warning(f"Attempted to emit event '{event}' but WebSocket is not connected")
    
    def connect(self):
        """Connect to the WebSocket server."""
        if not self.connected:
            try:
                logger.info(f"Connecting to WebSocket at {self.url}")
                self.sio.connect(self.url, wait_timeout=10)
            except Exception as e:
                logger.error(f"Failed to connect to WebSocket: {e}")
                self._schedule_reconnect()
    
    def disconnect(self):
        """Disconnect from the WebSocket server."""
        logger.info("Disconnecting WebSocket")
        self._stop_event.set()
        if self.connected:
            try:
                self.sio.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting WebSocket: {e}")
        self.connected = False
    
    def wait(self, seconds: Optional[float] = None):
        """Wait for SocketIO events."""
        self.sio.wait(seconds)
```

#### Usługa uwierzytelniania (services/auth_service.py)
```python
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .api_client import APIClient

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication with the AD backend."""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._refresh_threshold = timedelta(minutes=5)  # Refresh 5 minutes before expiry
    
    def login_device(self, device_id: str, device_secret: str) -> bool:
        """Authenticate a device and store the token."""
        try:
            auth_data = {
                'device_id': device_id,
                'device_secret': device_secret
            }
            # Assuming there's an auth endpoint for devices
            # Based on the backend analysis, this would be /api/v1/auth endpoint
            result = self.api_client._request_with_retry(
                'POST', 
                self.api_client._build_url('auth'), 
                json=auth_data
            )
            
            if result and 'access_token' in result:
                self._set_token(result['access_token'], result.get('expires_in', 1800))
                logger.info("Device authentication successful")
                return True
            else:
                logger.error("Device authentication failed: no token in response")
                return False
                
        except Exception as e:
            logger.error(f"Error during device authentication: {e}")
            return False
    
    def login_user(self, username: str, password: str) -> bool:
        """Authenticate a user and store the token."""
        try:
            auth_data = {
                'username': username,
                'password': password
            }
            result = self.api_client._request_with_retry(
                'POST', 
                self.api_client._build_url('auth/login'), 
                json=auth_data
            )
            
            if result and 'access_token' in result:
                self._set_token(result['access_token'], result.get('expires_in', 1800))
                logger.info("User authentication successful")
                return True
            else:
                logger.error("User authentication failed: no token in response")
                return False
                
        except Exception as e:
            logger.error(f"Error during user authentication: {e}")
            return False
    
    def _set_token(self, token: str, expires_in: int):
        """Set the authentication token."""
        self._token = token
        self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
        self.api_client.set_auth_token(token, expires_in)
    
    def clear_token(self):
        """Clear the authentication token."""
        self._token = None
        self._token_expiry = None
        self.api_client.clear_auth_token()
    
    def is_authenticated(self) -> bool:
        """Check if we have a valid authentication token."""
        return self._token is not None and \
               self._token_expiry is not None and \
               datetime.now() < self._token_expiry
    
    def needs_refresh(self) -> bool:
        """Check if token needs to be refreshed."""
        if not self.is_authenticated():
            return False
        
        time_until_expiry = self._token_expiry - datetime.now()
        return time_until_expiry <= self._refresh_threshold
    
    def refresh_token(self) -> bool:
        """Refresh the authentication token."""
        # This would require implementing a refresh token endpoint
        # For now, we'll just clear and require re-login
        logger.info("Token refresh not implemented, requiring re-login")
        self.clear_token()
        return False
```

### Pliki, które należy utworzyć lub zmodyfikowane
W ramach tej sekcji zostaną utworzone następujące pliki:

**Konfiguracja środowiska:**
- `/requirements.txt` - lista zależności Python
- `/.env.example` - przykładowy plik zmiennych środowiskowych
- `/.env` - rzeczywisty plik zmiennych środowiskowych (nie commitowany do repozytorium)

**Konfiguracja Flaska:**
- `/app/config/__init__.py` - pakiet konfiguracji
- `/app/config/default.py` - domyślna konfiguracja
- `/app/config/development.py` - konfiguracja rozwojowa
- `/app/config/testing.py` - konfiguracja testowa
- `/app/config/production.py` - konfiguracja produkcyjna

**Główna aplikacja:**
- `/app/app.py` - główna aplikacja Flask z factory pattern

**Warstwa usług:**
- `/app/services/__init__.py` - pakiet usług
- `/app/services/api_client.py` - klient komunikujący się z backend API
- `/app/services/websocket_service.py` - usługa WebSocket (opcjonalnie)
- `/app/services/auth_service.py` - usługa uwierzytelniania (opcjonalnie)
- `/app/services/data_processor.py` - przetwarzanie i formatowanie danych (do utworzenia w późniejszych sekcjach)

### Integracja z pozostałymi elementami systemu
Konfiguracja i środowisko zapewniają:
- Izolację środowisk (development, testing, production) poprzez różne konfiguracje
- Bezpieczne zarządzanie sekretami poprzez zmienne środowiskowe
- Elastyczność w konfiguracji różnych aspektów aplikacji
- Łatwe wdrażanie poprzez standardowe praktyki (12-factor app)
- Odporność na awarie poprzez mechanizmy ponawiania żądań
- Bezpieczeństwo poprzez odpowiednie zarządzanie sesjami i tokenami
- Wydajność poprzez opcjonalne cachowanie i efektywne połączenia
- Testowalność poprzez możliwość mockowania usług i konfiguracji testowych

### Obsługa błędów i przypadków brzegowych
Konfiguracja zawiera mechanizmy radzenia sobie z różnymi sytuacjami:

#### Błędy konfiguracji
- **Brak wymaganych zmiennych środowiskowych**: aplikacja powinna uruchomić się z wartościami domyślnymi i wyraźnym ostrzeżeniem w logach
- **Nieprawidłowe wartości**: walidacja podczas ładowania konfiguracji z wyraźnymi komunikatami o błędach
- **Niezgodne środowisko**: możliwość wymuszenia konkretnego środowiska poprzez FLASK_ENV

#### Błędy połączenia z backendem
- **Brak połączenia**: mechanizm ponawiania żądań z wykładniczym opóźnieniem
- **Timeout**: konfigurujemy timeout dla żądań i odpowiednie obsługi wyjątków
- **Błędy HTTP**: szczegółowa obsługa różnych kodów statusu (4xx, 5xx) z odpowiednimi działaniami
- **Nieprawidłowe odpowiedzi**: walidacja formatu JSON i struktury danych
- **WebSocket rozłączenia**: automatyczne ponawianie prób połączenia z ograniczoną liczbą prób

#### Błędy uwierzytelniania
- **Nieprawidłowe poświadczenia**: wyraźne komunikaty o błędach dla użytkownika
- **Wygasłe tokeny**: automatyczne wykrywanie i przekierowanie do logowania
- **Brak uprawnień**: obsługa błędów 403 i 401 z odpowiednimi komunikatomi
- **Odświeżanie tokenów**: mechanizm odświeżania tokenów przed ich wygaśnięciem (jeśli wspierane przez backend)

#### Błędy środowiskowe
- **Niedostępne zależności**: wyraźne komunikaty podczas uruchamiania aplikacji
- **Niezgodne wersje Python**: sprawdzenie wersji podczas uruchamiania
- **Problemy z uprawnieniami dostępu**: obsługa błędów systemowych podczas dostępu do plików lub zasobów

### Testy wymagane do uznania sekcji za ukończoną
- Zweryfikowanie, że wszystkie wymagane zależności są prawidłowo określone
- Potwierdzenie, że konfiguracja wspiera różne środowiska (development, testing, production)
- Dokumentacja wszystkich zmiennych środowiskowych i ich zastosowania
- Sprawdzenie, że klient API prawidłowo komunikuje się z backendem
- Weryfikacja mechanizmów ponawiania żądań i obsługi błędów
- Potwierdzenie, że usługa uwierzytelniania prawidłowo zarządza tokenami
- Sprawdzenie, że plik .env.example zawiera wszystkie niezbędne zmienne
- Potwierdzenie, że aplikacja może być uruchomiona w różnych środowiskach

### Jednoznaczne kryteria akceptacji
- Dokument zawiera kompletną listę zależności wymaganych dla aplikacji Flask
- Plik .env.example zawiera wszystkie niezbędne zmienne środowiskowe z przykładowymi wartościami
- Struktura konfiguracji wspiera różne środowiska aplikacji
- Klient API jest zaimplementowany z odpowiednimi mechanizmami ponawiania żądań
- Mechanizmy obsługi błędów są odpowiednio zdefiniowane dla różnych scenariuszy
- Usługa uwierzytelniania jest przygotowana do zarządzania tokenami dostępu
- Dokumentacja zawiera jasne instru dotyczące konfiguracji środowiska
- Konfiguracja jest zgodna z zasadami 12-factor app i najlepszymi praktykami
- Wszystkie elementy konfiguracji są oparte na rzeczywistym backendzie API (nie wymyślono funkcjonalności)

### Zależności od innych sekcji
- Wymaga ukończenia: 01_PROJECT_ANALYSIS.md, 02_ARCHITECTURE.md
- Jest wymaganiem wstępnym dla: wszystkie sekcje implementacyjne (05-20)

### Warunki zakończenia prac
Uznać sekcję za zakończoną gdy:
- Utworzono kompletną listę zależności w requirements.txt
- Utworzono przykładowy plik .env.example z wszystkimi niezbędnymi zmiennymi
- Zdefiniowano strukturę konfiguracji wspierającą różne środowiska
- Zaimplementowano klient API z mechanizmami komunikacji z backendem
- Dokumentowano wszystkie zmienne środowiskowe i ich zastosowanie
- Zaplanowano integrację konfiguracji z aplikacją Flask
- Określono mechanizmy obsługi błędów i przypadków brzegowych
- Przygotowano podstawy dla usług uwierzytelniania i WebSocket (jeśli potrzebne)

### Informacje, które należy przekazać do kolejnych sekcji
- Lista zależności i instrukcje dotyczące ich instalacji
- Strukturę konfiguracji i sposób ładowania zmiennych środowiskowych
- Interfejs klienta API i dostępne metody
- Dostępność uwierzytelniania i WebSocket w backendzie
- Zmienne środowiskowe wymagane do działania aplikacji
- Mechanizmy obsługi błędów i ponawiania żądań
- Podejście do zarządzania sesjami i tokenami dostępu
- Instrukcje dotyczące uruchamiania aplikacji w różnych środowiskach