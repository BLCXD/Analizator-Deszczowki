"""
Analytics controller for Analizator Deszczówki.
"""
from urllib.parse import quote
import secrets
from flask import render_template, session, jsonify, request, current_app, make_response
from app.controllers.base import create_blueprint, login_required
from app.services.api_client import api_client, APIError
from app.rate_limit import SQLiteRateLimiter, request_bucket

analytics_bp = create_blueprint('analytics', __name__)


def _require_login():
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    return None


@analytics_bp.route('/')
@login_required
def index():
                         
    session.setdefault('analytics_csrf', secrets.token_urlsafe(32))
    return render_template('analytics.html', active_page='analytics', authenticated=True,
                           analytics_csrf=session['analytics_csrf'])


@analytics_bp.route('/api/ai/<device_id>', methods=['POST'])
def ai_measurement_analysis(device_id):
    denied = _require_login()
    if denied:
        return denied
    """Request an owner-checked, rate-limited analysis from the backend."""
    try:
        expected = session.get('analytics_csrf', '')
        supplied = request.headers.get('X-CSRF-Token', '')
        if not expected or not supplied or not secrets.compare_digest(expected, supplied):
            return jsonify({'error': 'Sesja formularza wygasła. Odśwież stronę i spróbuj ponownie.'}), 400

        hours = request.args.get('hours', 168, type=int)
        if hours is None or not 1 <= hours <= 720:
            return jsonify({'error': 'Zakres analizy musi wynosić od 1 do 720 godzin.'}), 400

        params = {'hours': hours}
        city = request.args.get('city', '').strip()
        if city:
            if len(city) > 120:
                return jsonify({'error': 'Nazwa miasta jest za długa.'}), 400
            params['city'] = city
        for coordinate in ('latitude', 'longitude'):
            value = request.args.get(coordinate, type=float)
            limit = 90 if coordinate == 'latitude' else 180
            if value is not None:
                if not -limit <= value <= limit:
                    return jsonify({'error': 'Nieprawidłowe współrzędne lokalizacji.'}), 400
                params[coordinate] = value
        if ('latitude' in params) != ('longitude' in params) or (city and 'latitude' in params):
            return jsonify({'error': 'Do analizy pogody potrzebne są obie współrzędne.'}), 400

        limiter = current_app.extensions.get('ai_analysis_rate_limiter')
        if limiter is None or str(limiter.database_path) != str(current_app.config['RATE_LIMIT_DB_PATH']):
            limiter = SQLiteRateLimiter(current_app.config['RATE_LIMIT_DB_PATH'])
            current_app.extensions['ai_analysis_rate_limiter'] = limiter
        account = session.get('username', 'authenticated-user')
        bucket = request_bucket(current_app.config['SECRET_KEY'], account, 'ai-analysis')
        allowed, retry_after = limiter.hit(bucket, current_app.config['AI_ANALYSIS_RATE_LIMIT'],
                                           current_app.config['AI_ANALYSIS_RATE_WINDOW_SECONDS'])
        if not allowed:
            response = make_response(jsonify({'error': 'Wykorzystano limit analiz AI. Spróbuj ponownie później.'}), 429)
            response.headers['Retry-After'] = str(retry_after)
            return response

        result = api_client.post(
            f'/api/v1/measurements/{quote(device_id, safe="")}/analysis/ai',
            params=params,
            timeout=85,
        )
        return jsonify(result)
    except APIError as exc:
        messages = {
            403: 'Nie masz dostępu do tego urządzenia.',
            404: 'Nie znaleziono urządzenia.',
            503: 'Analiza AI jest chwilowo niedostępna lub nie została skonfigurowana.',
            504: 'Analiza AI nie odpowiedziała na czas. Spróbuj ponownie później.',
        }
        return jsonify({'error': messages.get(exc.status_code, 'Nie udało się przygotować analizy AI.')}), exc.status_code or 502
    except Exception:
        current_app.logger.warning('AI analysis request failed')
        return jsonify({'error': 'Nie udało się połączyć z usługą analizy AI.'}), 502


@analytics_bp.route('/api/trends/<device_id>')
def measurement_trends(device_id):
    denied = _require_login()
    if denied:
        return denied
    """API endpoint to get measurement trends for a device."""
    try:
        hours = request.args.get('hours', 24, type=int)
        response = api_client.get(f'/api/v1/measurements/{quote(device_id, safe="")}/analysis/trends', params={'hours': hours})
        return jsonify(response)
    except APIError as e:
        return jsonify({'error': e.message}), e.status_code or 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in measurement_trends: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/api/anomalies/<device_id>')
def measurement_anomalies(device_id):
    denied = _require_login()
    if denied:
        return denied
    """API endpoint to get measurement anomalies for a device."""
    try:
        hours = request.args.get('hours', 24, type=int)
        response = api_client.get(f'/api/v1/measurements/{quote(device_id, safe="")}/analysis/anomalies', params={'hours': hours})
        return jsonify(response)
    except APIError as e:
        return jsonify({'error': e.message}), e.status_code or 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in measurement_anomalies: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/api/history/<device_id>')
def measurement_history(device_id):
    denied = _require_login()
    if denied:
        return denied
    try:
        result = api_client.get(
            f'/api/v1/measurements/{quote(device_id, safe="")}',
            params={'limit': 500},
        )
        return jsonify({'measurements': result})
    except APIError as exc:
        current_app.logger.warning('Analytics history request failed with status %s', exc.status_code)
        return jsonify({'error': 'Nie udało się pobrać historii pomiarów'}), exc.status_code or 502
