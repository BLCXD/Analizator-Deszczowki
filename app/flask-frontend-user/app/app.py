"""
Main Flask application factory for Analizator Deszczówki Dashboard.
"""
import os
import logging
import sys
from flask import Flask, jsonify, render_template, request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config

def create_app(config_name=None):
\
\
\
\
\
\
\
\
       
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    app.config.from_object(config[config_name])
    if config_name == 'production' and (not app.config.get('SECRET_KEY') or len(app.config['SECRET_KEY']) < 32):
        raise RuntimeError('SECRET_KEY must contain at least 32 characters in production')
    if config_name == 'production':
        from app.session_store import SQLiteSessionInterface
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.session_interface = SQLiteSessionInterface(
            os.environ.get('SESSION_DB_PATH', '/data/flask-sessions.sqlite')
        )
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    @app.get('/_health')
    def healthcheck():
        return {'status': 'ok'}

    if not app.debug and not app.testing:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Analizator Deszczówki Dashboard startup')


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

    from app.controllers.test_js import test_bp
    app.register_blueprint(test_bp)

    from app.controllers.simple_test import simple_test_bp
    app.register_blueprint(simple_test_bp)

    from app.controllers.settings import settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')

    from app.controllers.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.controllers.legal import legal_bp
    app.register_blueprint(legal_bp)

    register_error_handlers(app)

    @app.shell_context_processor
    def make_shell_context():
        return {'app': app}

    return app


def register_error_handlers(app):
                                                            

    error_messages = {
        400: ('Nieprawidłowe żądanie', 'Sprawdź wprowadzone dane i spróbuj ponownie.'),
        401: ('Wymagane logowanie', 'Zaloguj się, aby przejść dalej.'),
        403: ('Brak dostępu', 'Nie masz uprawnień do wyświetlenia tej strony.'),
        404: ('Nie znaleziono strony', 'Podany adres może być nieaktualny lub zawierać błąd.'),
        405: ('Niedozwolona metoda', 'Ta operacja nie jest dostępna pod tym adresem.'),
        500: ('Coś poszło nie tak', 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie za chwilę.'),
        502: ('Problem z połączeniem', 'Serwer otrzymał nieprawidłową odpowiedź. Spróbuj ponownie za chwilę.'),
        503: ('Serwis chwilowo niedostępny', 'Trwa krótka przerwa techniczna. Spróbuj ponownie za chwilę.'),
        504: ('Przekroczono czas oczekiwania', 'Serwer zbyt długo czekał na odpowiedź. Spróbuj ponownie.'),
    }

    def error_response(status, message):
        if request.path.startswith('/api/') or request.accept_mimetypes.best == 'application/json':
            return jsonify(error=message), status
        title, description = error_messages[status]
        return render_template('errors/error.html', status=status, title=title, description=description), status

    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f'Bad request: {error}')
        return error_response(400, 'Bad request')

    @app.errorhandler(401)
    def unauthorized_error(error):
        app.logger.warning(f'Unauthorized: {error}')
        return error_response(401, 'Unauthorized')

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'Forbidden: {error}')
        return error_response(403, 'Forbidden')

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'Not found: {error}')
        return error_response(404, 'Not found')

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        app.logger.warning(f'Method not allowed: {error}')
        return error_response(405, 'Method not allowed')

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server error: {error}')
        return error_response(500, 'Internal server error')

    @app.errorhandler(502)
    def bad_gateway_error(error):
        app.logger.error(f'Bad gateway: {error}')
        return error_response(502, 'Bad gateway')

    @app.errorhandler(503)
    def service_unavailable_error(error):
        app.logger.error(f'Service unavailable: {error}')
        return error_response(503, 'Service unavailable')

    @app.errorhandler(504)
    def gateway_timeout_error(error):
        app.logger.error(f'Gateway timeout: {error}')
        return error_response(504, 'Gateway timeout')

    @app.errorhandler(Exception)
    def unhandled_exception(error):
                                                                                         
        app.logger.exception(f'Unhandled exception: {error}')
        return error_response(500, 'Internal server error')
