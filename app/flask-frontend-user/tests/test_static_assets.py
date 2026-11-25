import os
import re
import tempfile
import unittest
import requests
from unittest.mock import patch, Mock
from datetime import datetime, timedelta, timezone
from flask import Flask, session

os.environ.setdefault('SECRET_KEY', 'test-only-secret')
os.environ.setdefault('FLASK_ENV', 'testing')

from app import app
from app.session_store import SQLiteSessionInterface


def test_rendered_pages_reference_available_css_assets():
    client = app.test_client()

    for path in ('/auth/login', '/auth/register'):
        response = client.get(path)

        assert response.status_code == 200
        assert b'href="/static/css/base.css"' in response.data
        assert b'css/style.css' not in response.data

    stylesheet = client.get('/static/css/base.css')

    assert stylesheet.status_code == 200
    assert stylesheet.content_type.startswith('text/css')
    assert b'--color-bg-primary' in stylesheet.data

    script = client.get('/static/js/main.js')

    assert script.status_code == 200
    assert b"if (!document.getElementById('backend-status'))" in script.data


class StaticAssetsTestCase(unittest.TestCase):
    def test_production_session_keeps_access_token_out_of_browser_cookie(self):
        with tempfile.TemporaryDirectory() as directory:
            test_app = Flask(__name__)
            test_app.secret_key = 'test-secret-with-at-least-32-characters'
            test_app.permanent_session_lifetime = timedelta(minutes=30)
            test_app.session_interface = SQLiteSessionInterface(os.path.join(directory, 'sessions.sqlite'))

            @test_app.get('/protected')
            def protected():
                return {'authenticated': session.get('authenticated', False)}

            @test_app.post('/rotate')
            def rotate():
                test_app.session_interface.regenerate(session)
                return {'rotated': True}

            client = test_app.test_client()
            with client.session_transaction() as sess:
                sess['authenticated'] = True
                sess['access_token'] = 'private-jwt-value'

            cookie = client.get_cookie(test_app.config['SESSION_COOKIE_NAME'])
            self.assertIsNotNone(cookie)
            self.assertNotIn('private-jwt-value', cookie.value)
            old_sid = cookie.value
            self.assertEqual(client.post('/rotate').status_code, 200)
            self.assertNotEqual(client.get_cookie(test_app.config['SESSION_COOKIE_NAME']).value, old_sid)
            self.assertEqual(client.get('/protected').get_json(), {'authenticated': True})

    def test_static_assets(self):
        test_rendered_pages_reference_available_css_assets()

    def test_unknown_route_returns_a_real_404_when_caching_is_enabled(self):
        client = app.test_client()
        with patch.dict(app.config, {'ENABLE_CACHING': True}):
            response = client.get('/api/v1/auth/login')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {'error': 'Not found'})

    def test_design_system_tokens_present(self):
        client = app.test_client()
        res = client.get('/static/css/base.css')
        self.assertEqual(res.status_code, 200)
        required_tokens = [
            b'--color-bg-primary',
            b'--color-surface',
            b'--color-text-primary',
            b'--color-accent',
            b'--color-status-success',
            b'--color-status-warning',
            b'--color-status-error',
            b'--color-status-info',
            b'--color-border',
            b'#0F1419',
            b'#393E44',
            b'#D4F4FF',
            b'#E49D22',
        ]
        for token in required_tokens:
            self.assertIn(token, res.data, f"Token {token} missing from base.css")

    def test_pages_render_without_errors(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['access_token'] = 'test-token'
            sess['username'] = 'test@ad.io'

        for route in ('/', '/measurements/', '/analytics/', '/devices/', '/settings/'):
            res = client.get(route, follow_redirects=True)
            self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")
            self.assertIn(b'href="/auth/logout"', res.data)
            self.assertIn('Wyloguj'.encode(), res.data)

    def test_logout_link_is_hidden_when_logged_out(self):
        response = app.test_client().get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'href="/auth/logout"', response.data)

    def test_legal_pages_render_and_cookie_notice_is_present(self):
        client = app.test_client()
        for path, heading in (
            ('/privacy', 'Polityka prywatności'),
            ('/cookies', 'Polityka plików cookies'),
            ('/terms', 'Regulamin usługi'),
            ('/eula', 'Umowa licencyjna użytkownika końcowego'),
        ):
            response = client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn(heading.encode(), response.data)
            self.assertIn(b'ad-cookie-notice', response.data)

    def test_dashboard_renders_measurements_with_missing_optional_sensor_values(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['access_token'] = 'test-token'

        timestamp = datetime.now(timezone.utc).isoformat()
        profile_response = Mock(status_code=200)
        profile_response.json.return_value = {'email': 'test@example.com'}
        devices_response = Mock(status_code=200)
        devices_response.json.return_value = [{'device_id': 'mock-001', 'name': 'Mockowy zbiornik'}]
        measurement_response = Mock(status_code=200)
        measurement_response.json.return_value = {
            'measurement_time': timestamp,
            'water_quality_ph': None,
            'water_quality_turbidity': None,
            'temperature': None,
            'humidity': None,
        }
        alerts_response = Mock(status_code=404)

        with patch('app.controllers.dashboard.requests.get', side_effect=[
            profile_response, devices_response, measurement_response, alerts_response,
        ]):
            response = client.get('/')

        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn('Mockowy zbiornik', page)
        self.assertIn('Dev Mode', page)
        self.assertNotIn('Backend API', page)
        self.assertNotIn('Baza danych', page)
        self.assertNotIn('Szybkie akcje', page)
        self.assertEqual(page.count('brak danych'), 4)
        self.assertGreaterEqual(len(re.findall(r'ad-metric-value" data-value="">\s*--', page)), 4)

    def test_dashboard_uses_empty_data_when_backend_is_unavailable(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['access_token'] = 'test-token'

        with patch('app.controllers.dashboard.requests.get', side_effect=requests.ConnectionError):
            response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_system_status_checks_health_and_updates_database_state(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['access_token'] = 'test-token'

        health_response = Mock(status_code=200)
        profile_response = Mock(status_code=200)
        with patch('app.controllers.dashboard.requests.get', side_effect=[health_response, profile_response]) as get:
            response = client.get('/api/system-status')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            'status': 'ok',
            'backend': 'connected',
            'database': 'connected',
            'websocket': 'connected',
            'online': True,
        })
        self.assertTrue(get.call_args_list[0].args[0].endswith('/health'))

    def test_password_reset_is_csrf_protected_and_token_stays_out_of_request_url(self):
        client = app.test_client()
        forgot = client.get('/auth/password-reset')
        self.assertEqual(forgot.status_code, 200)
        csrf = re.search(rb'name="csrf_token" value="([^"]+)"', forgot.data).group(1).decode()
        with patch('app.controllers.auth._auth_rate_limit_response', return_value=None):
            with patch('app.controllers.auth.requests.post', return_value=Mock(status_code=202)) as post:
                submitted = client.post('/auth/password-reset', data={
                    'csrf_token': csrf, 'email': 'reset@example.com',
                })
        self.assertEqual(submitted.status_code, 200)
        self.assertIn('Jeśli konto istnieje'.encode(), submitted.data)
        self.assertEqual(post.call_args.args[0].endswith('/api/v1/auth/password-reset/request'), True)

        token = 'sensitive-one-time-token-value'
        reset_page = client.get('/auth/password-reset/confirm')
        self.assertEqual(reset_page.status_code, 200)
        self.assertEqual(reset_page.headers['Cache-Control'], 'no-store')
        self.assertEqual(reset_page.headers['Referrer-Policy'], 'no-referrer')
        csrf = re.search(rb'name="csrf_token" value="([^"]+)"', reset_page.data).group(1).decode()
        with patch('app.controllers.auth._auth_rate_limit_response', return_value=None):
            with patch('app.controllers.auth.requests.post', return_value=Mock(status_code=200)) as post:
                changed = client.post('/auth/password-reset/confirm', data={
                    'csrf_token': csrf, 'token': token,
                    'password': 'New-Password-Rain-2026',
                    'confirm_password': 'New-Password-Rain-2026',
                })
        self.assertEqual(changed.status_code, 200)
        self.assertNotIn(token.encode(), changed.data)
        self.assertNotIn(token, post.call_args.args[0])
        self.assertEqual(post.call_args.kwargs['json']['token'], token)

    def test_measurement_proxy_uses_real_backend_data_and_requires_login(self):
        client = app.test_client()
        unauthorized = client.get('/measurements/api/latest/mock-001')
        self.assertEqual(unauthorized.status_code, 401)

        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['access_token'] = 'test-token'

        measurement = {'measurement_id': 'm1', 'ec': 310, 'water_quality_turbidity': 2.1}
        with patch('app.controllers.measurements.api_client.get', return_value=measurement) as get:
            response = client.get('/measurements/api/latest/mock-001')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), measurement)
        get.assert_called_once_with('/api/v1/measurements/mock-001/latest')

    def test_measurements_page_uses_session_proxy_instead_of_browser_auth_token(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['access_token'] = 'test-token'

        response = client.get('/measurements/')

        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("fetch('/devices/api/list'", page)
        self.assertNotIn('getAuthToken()', page)
        self.assertNotIn("fetch('/api/v1/devices/'", page)

    def test_ai_analysis_proxy_allows_nvidia_response_time(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['access_token'] = 'test-token'
            sess['username'] = 'ai-timeout-test@example.com'
            sess['analytics_csrf'] = 'csrf-test'

        with patch('app.controllers.analytics.api_client.post', return_value={'analysis': 'Gotowe'}) as post:
            response = client.post('/analytics/api/ai/mock-001?hours=24', headers={
                'X-CSRF-Token': 'csrf-test',
            })

        self.assertEqual(response.status_code, 200)
        post.assert_called_once_with(
            '/api/v1/measurements/mock-001/analysis/ai',
            params={'hours': 24},
            timeout=85,
        )

    def test_analytics_history_is_authenticated_and_uses_saved_measurements(self):
        client = app.test_client()
        self.assertEqual(client.get('/analytics/api/history/mock-001').status_code, 401)
        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['access_token'] = 'test-token'
        with patch('app.controllers.analytics.api_client.get', return_value=[{'measurement_id': 'm1'}]) as get:
            response = client.get('/analytics/api/history/mock-001')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'measurements': [{'measurement_id': 'm1'}]})
        get.assert_called_once_with('/api/v1/measurements/mock-001', params={'limit': 500})

    def test_logout_link_is_only_rendered_once_for_authenticated_users(self):
        client = app.test_client()

        login_page = client.get('/auth/login').get_data(as_text=True)
        self.assertNotIn('href="/auth/logout"', login_page)

        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['username'] = 'test@example.com'

        page = client.get('/settings/profile').get_data(as_text=True)
        self.assertEqual(page.count('href="/auth/logout"'), 1)
        self.assertIn('<span>Wyloguj</span>', page)

    def test_delete_device_proxy_calls_backend(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['access_token'] = 'test-token'

        with patch('app.controllers.devices.api_client.delete') as delete:
            response = client.delete('/devices/api/mock-001')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'success': True})
        delete.assert_called_once_with('/api/v1/devices/mock-001')

    def test_api_settings_are_hidden_without_dev_mode(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['user_settings'] = {'dev_mode': False}

        response = client.get('/settings/api')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/settings/profile', response.headers['Location'])

    def test_dev_mode_can_be_enabled_from_sidebar_toggle_endpoint(self):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['authenticated'] = True

        response = client.post('/settings/api/config', json={'dev_mode': True})

        self.assertEqual(response.status_code, 200)
        with client.session_transaction() as sess:
            self.assertTrue(sess['user_settings']['dev_mode'])


if __name__ == '__main__':
    unittest.main()
