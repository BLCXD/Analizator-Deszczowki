"""
Auth controller for Analizator Deszczówki.
"""
import requests
import secrets
from flask import render_template, session, request, redirect, url_for, flash, current_app, make_response, jsonify
from app.controllers.base import create_blueprint
from app.rate_limit import SQLiteRateLimiter, request_bucket

auth_bp = create_blueprint('auth', __name__)


def _auth_rate_limit_response(route, template=None):
    limiter = current_app.extensions.get('auth_rate_limiter')
    if limiter is None:
        limiter = SQLiteRateLimiter(current_app.config['RATE_LIMIT_DB_PATH'])
        current_app.extensions['auth_rate_limiter'] = limiter
    bucket = request_bucket(current_app.config['SECRET_KEY'], request.remote_addr, route)
    allowed, retry_after = limiter.hit(
        bucket,
        current_app.config['AUTH_RATE_LIMIT'],
        current_app.config['AUTH_RATE_WINDOW_SECONDS'],
    )
    if allowed:
        return None
    response = make_response(render_template(f'auth/{template or route}.html'), 429)
    response.headers['Retry-After'] = str(retry_after)
    return response


def _validate_csrf():
    expected = session.get('_csrf_token')
    supplied = request.form.get('csrf_token', '')
    valid = bool(expected and supplied and secrets.compare_digest(expected, supplied))
    session['_csrf_token'] = secrets.token_urlsafe(32)
    return valid


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
                     
    if request.method == 'POST':
        limited = _auth_rate_limit_response('login')
        if limited:
            return limited
        if not _validate_csrf():
            flash('Formularz wygasł. Odśwież stronę i spróbuj ponownie.', 'error')
            return render_template('auth/login.html'), 400
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            response = requests.post(
                f"{current_app.config['API_BASE_URL']}/api/v1/auth/login",
                data={'username': username, 'password': password},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=current_app.config['API_TIMEOUT']
            )

            if response.status_code == 200:
                token_data = response.json()
                rotate_session = getattr(current_app.session_interface, 'regenerate', None)
                if rotate_session:
                    rotate_session(session)
                session['authenticated'] = True
                session['access_token'] = token_data.get('access_token')
                session['token_type'] = token_data.get('token_type')
                session['username'] = username
                try:
                    me_response = requests.get(
                        f"{current_app.config['API_BASE_URL']}/api/v1/auth/me",
                        headers={'Authorization': f"Bearer {session.get('access_token')}"},
                        timeout=current_app.config['API_TIMEOUT'],
                    )
                    if me_response.status_code == 200:
                        session['is_admin'] = me_response.json().get('is_admin') is True
                    else:
                        session.pop('is_admin', None)
                except requests.RequestException:
                    session.pop('is_admin', None)
                flash('Pomyślnie zalogowano!', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                if response.status_code == 401:
                    flash('Niepoprawny adres e-mail lub hasło.', 'error')
                else:
                    error_data = response.json() if response.headers.get('content-type') == 'application/json' else {'detail': 'Unknown error'}
                    flash(f'Błąd logowania: {error_data.get("detail", "Nieznany błąd")}', 'error')
        except requests.exceptions.RequestException:
            current_app.logger.exception('Login API request failed')
            flash('Nie można połączyć się z serwerem. Spróbuj ponownie później.', 'error')
        except Exception:
            current_app.logger.exception('Unexpected login error')
            flash('Wystąpił błąd. Spróbuj ponownie później.', 'error')

    else:
        session['_csrf_token'] = secrets.token_urlsafe(32)
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
                            
    if request.method == 'POST':
        limited = _auth_rate_limit_response('register')
        if limited:
            return limited
        if not _validate_csrf():
            flash('Formularz wygasł. Odśwież stronę i spróbuj ponownie.', 'error')
            return render_template('auth/register.html'), 400
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password:
            flash('Wszystkie pola są wymagane', 'error')
        elif password != confirm_password:
            flash('Hasła nie są identyczne', 'error')
        elif len(password) < 12:
            flash('Hasło musi mieć przynajmniej 12 znaków', 'error')
        else:
            try:
                response = requests.post(
                    f"{current_app.config['API_BASE_URL']}/api/v1/auth/register",
                    json={
                        'email': email,
                        'password': password
                    },
                    timeout=current_app.config['API_TIMEOUT']
                )

                if response.status_code == 200:
                    flash('Konto zostało utworzone. Teraz możesz się zalogować.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    error_data = response.json() if response.headers.get('content-type') == 'application/json' else {'detail': 'Unknown error'}
                    flash(f'Błąd rejestracji: {error_data.get("detail", "Nieznany błąd")}', 'error')
            except requests.exceptions.RequestException:
                current_app.logger.exception('Registration API request failed')
                flash('Nie można połączyć się z serwerem. Spróbuj ponownie później.', 'error')
            except Exception:
                current_app.logger.exception('Unexpected registration error')
                flash('Wystąpił błąd. Spróbuj ponownie później.', 'error')

    else:
        session['_csrf_token'] = secrets.token_urlsafe(32)
    return render_template('auth/register.html')


@auth_bp.route('/password-reset', methods=['GET', 'POST'])
def password_reset_request():
    if request.method == 'GET':
        session['_csrf_token'] = secrets.token_urlsafe(32)
        return render_template('auth/password_reset.html')
    limited = _auth_rate_limit_response('password-reset', 'password_reset')
    if limited:
        return limited
    if not _validate_csrf():
        return render_template('auth/password_reset.html', error='Formularz wygasł. Odśwież stronę.'), 400
    try:
        response = requests.post(
            f"{current_app.config['API_BASE_URL']}/api/v1/auth/password-reset/request",
            json={'email': request.form.get('email', '')},
            timeout=current_app.config['API_TIMEOUT'],
        )
        if response.status_code != 202:
            return render_template('auth/password_reset.html', error='Nie udało się wysłać prośby. Spróbuj ponownie.'), 502
    except requests.RequestException:
        return render_template('auth/password_reset.html', error='Serwer jest chwilowo niedostępny.'), 502
    return render_template('auth/password_reset.html', submitted=True)


@auth_bp.route('/password-reset/confirm', methods=['GET', 'POST'])
def password_reset_confirm():
    token = '' if request.method == 'GET' else request.form.get('token', '')
    if request.method == 'GET':
        session['_csrf_token'] = secrets.token_urlsafe(32)
        response = make_response(render_template('auth/password_reset_confirm.html', token=token))
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response
    limited = _auth_rate_limit_response('password-reset', 'password_reset_confirm')
    if limited:
        limited.headers['Cache-Control'] = 'no-store'
        limited.headers['Referrer-Policy'] = 'no-referrer'
        return limited
    if not _validate_csrf():
        return render_template('auth/password_reset_confirm.html', token=token, error='Formularz wygasł. Odśwież stronę.'), 400
    password = request.form.get('password', '')
    if len(password) < 12 or len(password.encode('utf-8')) > 72:
        return render_template('auth/password_reset_confirm.html', token=token, error='Hasło musi mieć od 12 do 72 bajtów.'), 400
    if password != request.form.get('confirm_password', ''):
        return render_template('auth/password_reset_confirm.html', token=token, error='Wpisane hasła nie są identyczne.'), 400
    try:
        response = requests.post(
            f"{current_app.config['API_BASE_URL']}/api/v1/auth/password-reset/confirm",
            json={'token': token, 'new_password': password},
            timeout=current_app.config['API_TIMEOUT'],
        )
        if response.status_code != 200:
            return render_template('auth/password_reset_confirm.html', token='', error='Link resetu jest nieprawidłowy lub wygasł.'), 400
    except requests.RequestException:
        return render_template('auth/password_reset_confirm.html', token='', error='Serwer jest chwilowo niedostępny.'), 502
    session.clear()
    response = make_response(render_template('auth/password_reset_confirm.html', token='', completed=True))
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


@auth_bp.route('/api/login-with-backend-token', methods=['POST'])
def login_with_backend_token():
    """Establish a Flask session from a backend JWT issued by the Pi login page.

    Used so the local Raspberry Pi login page (port 8000) can authenticate the user
    against the existing AD backend API and then auto-connect them to their local
    dashboard. The backend token is verified by calling /api/v1/auth/me; it is never
    stored in a file or logged.
    """
    import requests

    data = request.get_json(silent=True) or {}
    backend_token = data.get('access_token', '').strip()
    if not backend_token:
        return jsonify({'error': 'Backend token is required'}), 400

    try:
        me_response = requests.get(
            f"{current_app.config['API_BASE_URL']}/api/v1/auth/me",
            headers={'Authorization': f'Bearer {backend_token}'},
            timeout=current_app.config['API_TIMEOUT'],
        )
    except requests.exceptions.RequestException:
        current_app.logger.exception('Backend /me verification failed')
        return jsonify({'error': 'Nie można zweryfikować tokena z serwerem AD.'}), 502

    if me_response.status_code != 200:
        return jsonify({'error': 'Nieprawidłowy token sesji.'}), 401

    rotate_session = getattr(current_app.session_interface, 'regenerate', None)
    if rotate_session:
        rotate_session(session)
    session['authenticated'] = True
    session['access_token'] = backend_token
    session['token_type'] = 'bearer'
    user_data = me_response.json()
    session['username'] = user_data.get('email')
    session['is_admin'] = user_data.get('is_admin') is True

    return jsonify({'ok': True, 'redirect': url_for('dashboard.index')})


@auth_bp.route('/logout')
def logout():

    session.clear()
    flash('Zostałeś wylogowany', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
def profile():
                            
    if not session.get('authenticated'):
        return redirect(url_for('auth.login'))

    try:
        headers = {
            'Authorization': f"Bearer {session.get('access_token')}"
        }
        response = requests.get(
            f"{current_app.config['API_BASE_URL']}/api/v1/auth/me",
            headers=headers,
            timeout=current_app.config['API_TIMEOUT']
        )

        if response.status_code == 200:
            user_data = response.json()
            return render_template('auth/profile.html', user=user_data)
        else:
            flash('Nie można pobrać danych profilu', 'error')
            return redirect(url_for('dashboard.index'))
    except Exception as e:
        flash(f'Błąd połączenia z serwerem: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))
