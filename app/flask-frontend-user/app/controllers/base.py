"""
Base controller class with common functionality.
"""
from flask import Blueprint, current_app, request, session, jsonify, redirect, url_for
from functools import wraps
import logging

from app.i18n import t, get_available_languages, TRANSLATIONS
from functools import partial

logger = logging.getLogger(__name__)


def create_blueprint(name, import_name, url_prefix=None):
\
\
\
\
\
\
\
\
\
\
       
    bp = Blueprint(name, import_name, url_prefix=url_prefix)

    @bp.app_context_processor
    def inject_common_vars():
        lang = session.get('user_settings', {}).get('language', 'pl')
        return {
            'app_name': 'Analizator Deszczówki',
            'app_version': '0.1.0',
            'current_year': 2026,
            't': partial(t, lang=lang),
            'current_lang': lang,
            'available_languages': get_available_languages(),
            'js_translations': TRANSLATIONS.get('en', {}),
        }

    return bp


def login_required(f):
\
\
       
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        if 'is_admin' not in session:
            import requests
            try:
                response = requests.get(
                    f"{current_app.config['API_BASE_URL']}/api/v1/auth/me",
                    headers={'Authorization': f"Bearer {session.get('access_token')}"},
                    timeout=current_app.config['API_TIMEOUT'],
                )
                session['is_admin'] = response.json().get('is_admin') is True if response.status_code == 200 else False
            except requests.RequestException:
                session['is_admin'] = False
        return f(*args, **kwargs)
    return decorated_function


def api_key_required(f):
\
\
       
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config.get('API_KEY'):
            if request.is_json:
                return jsonify({'error': 'Valid API key required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def handle_api_errors(f):
\
\
       
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {f.__name__}: {str(e)}", exc_info=True)
            if request.is_json:
                return jsonify({'error': 'Internal server error'}), 500
            raise
    return decorated_function
