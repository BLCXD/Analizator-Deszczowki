"""
Settings controller for Analizator Deszczówki.
"""
from flask import render_template, session, jsonify, request, redirect, url_for, flash, current_app
import secrets
import requests
from app.controllers.base import create_blueprint, login_required
from app.services.api_client import APIClient, APIError

settings_bp = create_blueprint('settings', __name__)

api_client = APIClient()


def is_dev_mode_enabled():
                                                                            
    return bool(session.get('user_settings', {}).get('dev_mode', False))


@settings_bp.route('/')
@login_required
def index():
                                                              
    return redirect(url_for('settings.profile'))


@settings_bp.route('/profile')
@login_required
def profile():
                                     
    if not session.get('_csrf_token'):
        session['_csrf_token'] = secrets.token_urlsafe(32)
    headers = {'Authorization': f"Bearer {session.get('access_token')}"}
    try:
        response = requests.get(f"{current_app.config['API_BASE_URL']}/api/v1/auth/me", headers=headers,
                                timeout=current_app.config['API_TIMEOUT'])
        response.raise_for_status()
        user_data = response.json()
    except requests.RequestException:
        flash('Nie można pobrać danych profilu. Spróbuj ponownie później.', 'error')
        user_data = {}
    return render_template('settings/index.html',
                         active_page='settings',
                         authenticated=True,
                         active_settings='profile',
                         current_user=user_data)


@settings_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    supplied = request.form.get('csrf_token', '')
    if not supplied or not secrets.compare_digest(supplied, session.get('_csrf_token', '')):
        flash('Formularz wygasł. Odśwież stronę i spróbuj ponownie.', 'error')
        return redirect(url_for('settings.profile'))
    new_password = request.form.get('new_password', '')
    if new_password and new_password != request.form.get('confirm_password', ''):
        flash('Nowe hasła nie są identyczne.', 'error')
        return redirect(url_for('settings.profile'))
    payload = {
        'first_name': request.form.get('first_name', '').strip(),
        'last_name': request.form.get('last_name', '').strip(),
        'phone': request.form.get('phone', '').strip(),
        'current_password': request.form.get('current_password') or None,
        'new_password': new_password or None,
    }
    try:
        response = requests.patch(
            f"{current_app.config['API_BASE_URL']}/api/v1/auth/me", json=payload,
            headers={'Authorization': f"Bearer {session.get('access_token')}"},
            timeout=current_app.config['API_TIMEOUT'])
        if response.status_code == 200:
            flash('Dane profilu zostały zapisane.', 'success')
        else:
            try:
                detail = response.json().get('detail', 'Nie udało się zapisać profilu.')
            except ValueError:
                detail = 'Nie udało się zapisać profilu.'
            flash(detail, 'error')
    except requests.RequestException:
        flash('Serwer jest chwilowo niedostępny. Zmiany nie zostały zapisane.', 'error')
    return redirect(url_for('settings.profile'))


@settings_bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    supplied = request.form.get('csrf_token', '')
    if not supplied or not secrets.compare_digest(supplied, session.get('_csrf_token', '')):
        if request.is_json:
            return jsonify({'error': 'Formularz wygasł. Odśwież stronę i spróbuj ponownie.'}), 400
        flash('Formularz wygasł. Odśwież stronę i spróbuj ponownie.', 'error')
        return redirect(url_for('settings.profile'))

    try:
        api_client.delete(
            '/api/v1/auth/me',
            headers={'Authorization': f"Bearer {session.get('access_token')}"},
        )
    except APIError as exc:
        if exc.status_code == 401:
            session.clear()
            flash('Zostałeś wylogowany. Zaloguj się ponownie.', 'error')
            return redirect(url_for('auth.login'))
        current_app.logger.error(f"Failed to delete account: {exc.message}")
        flash(f"{t('Nie udało się usunąć konta: ')}{exc.message}", 'error')
        return redirect(url_for('settings.profile'))
    except requests.RequestException:
        current_app.logger.exception('Failed to connect to API while deleting account')
        flash('Serwer jest chwilowo niedostępny. Konto nie zostało usunięte.', 'error')
        return redirect(url_for('settings.profile'))

    session.clear()
    flash(t('Konto zostało usunięte. Zostałeś wylogowany.'), 'success')
    return redirect(url_for('auth.login'))


@settings_bp.route('/devices')
@login_required
def devices():
                                          
    return render_template('settings/index.html',
                         active_page='settings',
                         authenticated=True,
                         active_settings='devices')


@settings_bp.route('/notifications')
@login_required
def notifications():
                                     
    return render_template('settings/index.html',
                         active_page='settings',
                         authenticated=True,
                         active_settings='notifications')


@settings_bp.route('/appearance')
@login_required
def appearance():
                                             
    return render_template('settings/index.html',
                         active_page='settings',
                         authenticated=True,
                         active_settings='appearance')


@settings_bp.route('/api')
@login_required
def api_settings():
                                          
    if not is_dev_mode_enabled():
        return redirect(url_for('settings.profile'))

    api_config = session.get('api_config', {
        'api_url': 'http://localhost:8000',
        'timeout': 10,
        'retries': 3,
        'ssl_verify': True
    })
    return render_template('settings/index.html',
                         active_page='settings',
                         authenticated=True,
                         active_settings='appearance',
                         api_base_url=api_config.get('api_url'),
                         websocket_url=current_app.config.get('WS_URL', 'ws://localhost:8000/api/v1/measurements/ws'))


@settings_bp.route('/api/config')
@login_required
def get_config():
                                                    
    config = session.get('user_settings', {
        'refresh_interval': 30000,
        'enable_websocket': True,
        'demo_mode': False,
        'items_per_page': 20,
        'chart_height': 400,
        'theme': 'light',
        'language': 'pl',
        'date_format': 'YYYY-MM-DD',
        'time_format': 'HH:mm',
        'chart_animation': True,
        'compact_mode': False,
        'email_notifications': True,
        'push_notifications': False,
        'sms_notifications': False,
        'notify_anomalies': True,
        'notify_device_offline': True,
        'notify_maintenance': True,
        'notification_frequency': 'immediate',
        'auto_add_devices': True,
        'device_notifications': True,
        'device_refresh_interval': 30,
        'dev_mode': False
    })
    return jsonify(config)


@settings_bp.route('/api/lang', methods=['POST'])
@login_required
def update_lang():
                                                     
    data = request.get_json(silent=True) or {}
    if not data:
        data = request.form
    language = data.get('language')
    if language not in ('pl', 'en'):
        return jsonify({'success': False, 'message': 'Unsupported language'}), 400
    if 'user_settings' not in session:
        session['user_settings'] = {}
    session['user_settings']['language'] = language
    session.modified = True
    return jsonify({'success': True, 'language': language})


@settings_bp.route('/api/config', methods=['POST'])
@login_required
def update_config():
                                               
    try:
        data = request.get_json()

        if 'user_settings' not in session:
            session['user_settings'] = {}

        allowed_keys = [
            'refresh_interval', 'enable_websocket', 'demo_mode', 'items_per_page', 'chart_height',
            'theme', 'language', 'date_format', 'time_format', 'chart_animation', 'compact_mode',
            'email_notifications', 'push_notifications', 'sms_notifications', 'notify_anomalies',
            'notify_device_offline', 'notify_maintenance', 'notification_frequency',
            'auto_add_devices', 'device_notifications', 'device_refresh_interval',
            'dev_mode'
        ]

        for key in allowed_keys:
            if key in data:
                value = data[key]
                if key in {'dev_mode', 'enable_websocket', 'demo_mode', 'chart_animation',
                           'compact_mode', 'email_notifications', 'push_notifications',
                           'sms_notifications', 'notify_anomalies', 'notify_device_offline',
                           'notify_maintenance', 'auto_add_devices',
                           'device_notifications'}:
                    value = value is True or str(value).lower() in {'true', '1', 'on'}
                session['user_settings'][key] = value

        session.modified = True

        return jsonify({'success': True, 'message': 'Configuration updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@settings_bp.route('/push/vapid-public-key')
@login_required
def push_vapid_public_key():
                                                                       
    try:
        data = api_client.get('/api/v1/push/vapid-public-key')
        return jsonify(data), 200
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502


@settings_bp.route('/push/subscribe', methods=['POST', 'DELETE'])
@login_required
def push_subscribe():
                                                             
    try:
        data = request.get_json(silent=True) or {}
        if request.method == 'POST':
            resp = api_client.post('/api/v1/push/subscribe', data=data)
        else:
            resp = api_client.delete('/api/v1/push/subscribe', json=data)
        return jsonify(resp), 200
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502


@settings_bp.get('/push-sw.js')
@login_required
def push_service_worker():
                                                                                      
    response = current_app.send_static_file('js/push-sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache'
    return response


@settings_bp.route('/api/test-connection', methods=['POST'])
@login_required
def test_api_connection():
                                              
    try:
        data = request.get_json()
        api_url = data.get('api_url', 'http://localhost:8000')

        import requests
        from requests.exceptions import RequestException

        test_url = f"{api_url.rstrip('/')}/health"
        response = requests.get(test_url, timeout=5)

        if response.status_code == 200:
            if 'api_config' not in session:
                session['api_config'] = {}
            session['api_config']['api_url'] = api_url
            session.modified = True

            return jsonify({'success': True, 'message': 'Połączenie z API nawiązane pomyślnie'})
        else:
            return jsonify({'success': False, 'message': f'API returned status {response.status_code}'}), 400

    except RequestException as e:
        return jsonify({'success': False, 'message': f'Nie można połączyć się z API: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Błąd podczas testowania połączenia: {str(e)}'}), 400


@settings_bp.route('/api/diagnostics')
@login_required
def diagnostics():
                                                                           
    if not is_dev_mode_enabled():
        return jsonify({'error': 'Developer mode is disabled'}), 403

    import requests
    api_url = session.get('api_config', {}).get(
        'api_url', current_app.config.get('API_BASE_URL', 'http://localhost:8000')
    )
    device_id = None
    try:
        response = requests.get(f"{api_url.rstrip('/')}/health", timeout=5)
        backend = 'connected' if response.status_code == 200 else 'error'
        status_code = response.status_code
        if backend == 'connected':
            devices = api_client.get('/api/v1/devices/')
            if devices:
                device_id = devices[0].get('device_id')
    except requests.RequestException:
        backend = 'offline'
        status_code = None

    return jsonify({
        'backend': backend,
        'backend_url': api_url,
        'status_code': status_code,
        'websocket_url': current_app.config.get('WS_URL', 'ws://localhost:8000/api/v1/measurements/ws').rstrip('/')
            + (f"/{device_id}" if device_id else ''),
    })
